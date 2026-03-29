from django.urls import path
from web import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Partials
    path('partials/book-grid/', views.book_list_partial, name='book_list_partial'),
    path('partials/active-loans/', views.active_loans_partial, name='active_loans_partial'),
    path('calculate-deposit/', views.calculate_deposit_preview, name='calc_deposit'),

    # Modal Form Fetch
    path('books/<int:pk>/issue/', views.issue_book_form, name='issue_book_form'),
    
    # Modal Form Submission
    path('books/<int:pk>/issue/submit/', views.issue_book_submit, name='issue_book_submit'),

    path('loans/<int:pk>/return/form/', views.return_book_form, name='return_book_form'),
    path('loans/<int:pk>/return/submit/', views.return_book_submit, name='return_book_submit'),
]