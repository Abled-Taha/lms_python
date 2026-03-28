from web.decorators import manager_required
from django.shortcuts import render

@manager_required
def dashboard(request):
    return render(request, "dashboard.html")

def home(request):
    return render(request, "home.html")