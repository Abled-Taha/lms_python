from django.urls import path
from web import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # # Book Section
    # path('books/', include([
    #     path('', views.book_list, name='book_list'),
    #     path('<int:pk>/', views.book_detail, name='book_detail'),
    # ])),
    
    # # Issue Section
    # path('issue/', include([
    #     path('new/', views.issue_book, name='issue_book'),
    #     path('active/', views.active_issues, name='active_issues'),
    # ])),
]