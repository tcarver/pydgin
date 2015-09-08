from django.shortcuts import render


def index(request):
    ''' Renders a front page. '''
    return render(request, 'front_page.html', {}, content_type='text/html')
