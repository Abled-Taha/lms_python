from datetime import date, timedelta
from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .services import post_issue_actions

class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    
    # Tracking stock
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(0)]
    )
    
    # Metadata for the Manager
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.author.name})"

    class Meta:
        ordering = ['-added_at']

    def issue_to_borrower(self, manager, borrower_data):
        """
        Handles the database transaction for issuing a book.
        """
        if self.available_copies <= 0:
            raise ValueError("No copies of this book are currently available.")

        with transaction.atomic():
            # 1. Create the Issue Record
            from .models import BookIssue # Local import to avoid circular dependency
            issue = BookIssue.objects.create(
                book=self,
                issued_by=manager,
                **borrower_data
            )

            # 2. Update Stock
            self.available_copies -= 1
            self.save()

            # 3. Trigger Service Layer for side-effects
            post_issue_actions(issue)
            
            return issue

class BookIssue(models.Model):
    # Link to the book and the Manager who processed it
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name="issues")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Borrower Details
    borrower_name = models.CharField(max_length=255)
    # Pakistani CNIC format: 12345-1234567-1
    cnic_validator = RegexValidator(
        regex=r'^\d{5}-\d{7}-\d{1}$',
        message="CNIC must be in the format: 42101-1234567-1"
    )
    borrower_cnic = models.CharField(max_length=15, validators=[cnic_validator])
    borrower_phone = models.CharField(max_length=15) # e.g., +923001234567
    borrower_email = models.EmailField()
    
    # Financials
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    damage_notes = models.TextField(blank=True, null=True, help_text="Describe the damage observed")
    is_deposit_returned = models.BooleanField(default=False)
    
    # Dates
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    damage_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} -> {self.borrower_name}"
    
    def mark_as_returned(self):
        """
        Handles the return logic: updates stock and marks record as closed.
        """
        if self.is_returned:
            return # Already returned

        with transaction.atomic():
            # 1. Update the Issue record
            self.is_returned = True
            self.returned_at = timezone.now()
            self.is_deposit_returned = True
            self.save()

            # 2. Add stock back to the Book
            self.book.available_copies += 1
            self.book.save()
    
    def clean(self):
        """Custom validation for borrower limits and dates."""
        # 1. Check if borrower already has an active book
        active_loan = BookIssue.objects.filter(
            borrower_cnic=self.borrower_cnic, 
            is_returned=False
        ).exclude(pk=self.pk).exists()
        
        if active_loan:
            raise ValidationError(f"This borrower (CNIC: {self.borrower_cnic}) already has an unreturned book.")

        # 2. Max 1 month duration
        max_date = date.today() + timedelta(days=30)
        if self.due_date > max_date:
            raise ValidationError("Maximum checkout duration is 30 days.")
        
    def calculate_issuance_deposit(self):
        """Calculates Rs. 100/day for the chosen duration."""
        days = (self.due_date - date.today()).days
        return max(0, days * 100)

    def calculate_return_refund(self):
        """Subtracts Rs. 100/day for late returns and damage costs."""
        today = date.today()
        refund = self.deposit_amount # This is a Decimal
        
        # 1. Handle Late Penalty
        if today > self.due_date:
            overdue_days = (today - self.due_date).days
            # Convert the math result to Decimal
            late_penalty = Decimal(overdue_days) * Decimal('100.00')
            refund -= late_penalty
        
        # 2. Handle Damage Deduction
        # Ensure damage_deduction is treated as Decimal (it usually is if it's a model field)
        refund -= self.damage_deduction
        
        # Return 0 if the penalties exceed the deposit
        return max(Decimal('0.00'), refund)