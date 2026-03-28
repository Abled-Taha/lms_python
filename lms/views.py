from django.shortcuts import redirect

def redirect_to_web(request):
    return redirect('web/')