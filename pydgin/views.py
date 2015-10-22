from django.shortcuts import render


def index(request):
    ''' Renders a front page. '''
    return render(request, 'www-fp.html', {}, content_type='text/html')
