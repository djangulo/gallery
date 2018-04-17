from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def home(request):
    return render(request, 'home/home.bundle.html')
