from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import requests


# Create your views here.

def home(request):
    return render(request, 'base.html')

@csrf_exempt
def new_search(request):
    searches = request.POST.get('search')
    front_end = {
        'searching': searches,
    }
    return render(request, 'myapp/new_search.html', front_end)
