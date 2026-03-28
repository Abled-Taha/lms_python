from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 1. Check if they are even logged in
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        # 2. Check if they have the Manager (Staff) flag
        if not request.user.is_staff:
            logout(request) # <--- Kill the session immediately
            messages.error(request, "Invalid account type. Only staff accounts are permitted.")
            return redirect('account_login')
            
        return view_func(request, *args, **kwargs)
    return wrapper