from django.contrib import admin
from .models import Author, Book, BookIssue

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'available_copies', 'total_copies', 'isbn')
    list_filter = ('author',)
    search_fields = ('title', 'isbn')
    # This makes 'available_copies' read-only in admin if you want 
    # it handled only by logic later
    # readonly_fields = ('available_copies',)

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    # What columns to show in the list view
    list_display = (
        'book', 
        'borrower_name', 
        'borrower_cnic', 
        'deposit_amount', 
        'issued_at', 
        'due_date', 
        'is_returned'
    )
    
    # Add a sidebar to filter by these fields
    list_filter = ('is_returned', 'issued_at', 'due_date')
    
    # Add a search bar for Name or CNIC
    search_fields = ('borrower_name', 'borrower_cnic', 'book__title')
    
    # Make some fields read-only so they can't be accidentally edited
    readonly_fields = ('issued_at', 'returned_at', 'issued_by')

    # Optional: Group fields into sections when clicking into a record
    fieldsets = (
        ('Book Info', {
            'fields': ('book', 'issued_by')
        }),
        ('Borrower Details', {
            'fields': ('borrower_name', 'borrower_cnic', 'borrower_email', 'borrower_phone')
        }),
        ('Financials', {
            'fields': ('deposit_amount', 'is_deposit_returned')
        }),
        ('Status', {
            'fields': ('issued_at', 'due_date', 'returned_at', 'is_returned')
        }),
    )