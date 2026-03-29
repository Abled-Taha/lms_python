from datetime import date
from decimal import Decimal
from web.decorators import manager_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from core.models import Book, BookIssue
from .forms import BookIssueForm

@manager_required
def dashboard(request):
    books = Book.objects.all()
    loans = BookIssue.objects.filter(is_returned=False).order_by('due_date')
    return render(request, "dashboard.html", {
        'books': books,
        'loans': loans,
    })

def home(request):
    return render(request, "home.html")

@manager_required
def book_list_partial(request):
    """Returns only the HTML for the book grid."""
    books = Book.objects.all()
    return render(request, 'partials/book_list.html', {'books': books})

@manager_required
def issue_book_form(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookIssueForm()
    response = render(request, 'partials/issue_form.html', {'book': book, 'form': form})
    response['HX-Trigger'] = 'open-modal'
    return response

@manager_required
def issue_book_submit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == "POST":
        form = BookIssueForm(request.POST)
        if form.is_valid():
            try:
                # 🚀 Call the Fat Model method we built earlier
                book.issue_to_borrower(request.user, form.cleaned_data)
                
                # Success: Close modal and refresh the background list
                response = HttpResponse('<div class="p-4 text-green-700 bg-green-100 rounded-lg">Book Issued Successfully!</div>')
                response['HX-Trigger'] = 'close-modal, refresh-book-list'
                return response
            except ValueError as e:
                return HttpResponse(f'<p class="text-red-600 p-2">{str(e)}</p>')
        
        # If form is NOT valid, re-render the form with errors inside the modal
        return render(request, 'partials/issue_form.html', {'book': book, 'form': form})

@manager_required
def active_loans_partial(request):
    """Returns only the HTML for the active loans table."""
    loans = BookIssue.objects.filter(is_returned=False).order_by('due_date')
    return render(request, 'partials/active_loans_list.html', {'loans': loans})

@manager_required
def active_loans(request):
    # Show unreturned books first, ordered by due date (soonest first)
    loans = BookIssue.objects.filter(is_returned=False).order_by('due_date')
    return render(request, 'active_loans.html', {'loans': loans})

@manager_required
def calculate_deposit_preview(request):
    due_date_str = request.POST.get('due_date')
    if due_date_str:
        due_date = date.fromisoformat(due_date_str)
        days = (due_date - date.today()).days
        deposit = max(0, days * 100)
        return HttpResponse(f'<input type="number" name="deposit_amount" value="{deposit}" readonly class="bg-gray-100 cursor-not-allowed w-full rounded-lg p-2 border">')
    return HttpResponse('<input type="number" name="deposit_amount" readonly value="0">')

@manager_required
def return_book_form(request, pk):
    loan = get_object_or_404(BookIssue, pk=pk)
    today = date.today()
    overdue_days = (today - loan.due_date).days if today > loan.due_date else 0
    
    context = {
        'loan': loan,
        'overdue_days': overdue_days,
        'late_penalty': overdue_days * 100
    }
    response = render(request, 'partials/return_form.html', context)
    response['HX-Trigger'] = 'open-modal'
    return response

@manager_required
def return_book_submit(request, pk):
    loan = get_object_or_404(BookIssue, pk=pk)
    if request.method == "POST":
        loan = get_object_or_404(BookIssue, pk=pk)
    
        damage_raw = request.POST.get('damage_deduction', '0')
        loan.damage_deduction = Decimal(damage_raw or '0')
        
        loan.damage_notes = request.POST.get('damage_notes', '')
        
        # Now the math inside the model will work perfectly
        loan.final_refund_amount = loan.calculate_return_refund()
        loan.mark_as_returned()
        
        response = HttpResponse(f'''
            <div class="text-center p-6">
                <div class="text-emerald-500 text-5xl mb-4">✅</div>
                <h3 class="text-lg font-bold">Return Successful</h3>
                <p class="text-slate-500">Refunded: Rs. {loan.final_refund_amount}</p>
            </div>
        ''')
        response['HX-Trigger'] = 'close-modal, refresh-book-list'
        return response