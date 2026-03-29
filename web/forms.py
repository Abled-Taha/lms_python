import re
from datetime import date, timedelta
from django import forms
from django.core.validators import RegexValidator
from core.models import BookIssue

class BookIssueForm(forms.ModelForm):
    # CNIC Validator: 5 digits - 7 digits - 1 digit
    cnic_validator = RegexValidator(
        regex=r'^\d{5}-\d{7}-\d{1}$',
        message="CNIC must be in the format: 42101-1234567-1"
    )

    borrower_cnic = forms.CharField(
        validators=[cnic_validator],
        widget=forms.TextInput(attrs={'placeholder': '42101-1234567-1'})
    )

    class Meta:
        model = BookIssue
        fields = [
            'borrower_name', 'borrower_cnic', 'borrower_email', 
            'borrower_phone', 'deposit_amount', 'due_date'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'deposit_amount': forms.NumberInput(attrs={'placeholder': 'Rs.'}),
        }

    def clean_borrower_phone(self):
        phone = self.cleaned_data.get('borrower_phone')
        # Remove any accidental spaces or dashes
        clean_phone = re.sub(r'\D', '', phone)
        
        if len(clean_phone) != 11:
            raise forms.ValidationError("Phone number must be exactly 11 digits (e.g., 03001234567).")
        
        return clean_phone

    def clean_borrower_cnic(self):
        cnic = self.cleaned_data.get('borrower_cnic')
        # Ensure it matches the format 00000-0000000-0
        if not re.match(r'^\d{5}-\d{7}-\d{1}$', cnic):
            raise forms.ValidationError("Invalid CNIC format. Use 12345-1234567-1.")
        return cnic
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if not due_date:
            return due_date

        max_date = date.today() + timedelta(days=30)
        
        if due_date < date.today():
            raise forms.ValidationError("The due date cannot be in the past.")
            
        if due_date > max_date:
            # This error will now show up specifically under the due_date input
            raise forms.ValidationError("Maximum checkout duration is 30 days.")
            
        return due_date