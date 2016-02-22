from django.shortcuts import render
from django.conf import settings


def index(request):
    ''' Renders a front page. '''
    return render(request, 'front_page.html', {'CDN': settings.CDN}, content_type='text/html')
