"""
URL configuration for lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView
from django.conf import settings
from lms import views

urlpatterns = [
    re_path(r'^favicon\.ico$', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.png'), permanent=True)),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('web/', include('web.urls')),
    path('', views.redirect_to_web),
]

if settings.DEBUG:
    # Include django browser reload URLs only in debug mode
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls")),]