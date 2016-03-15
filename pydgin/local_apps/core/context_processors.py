''' Context processors that are used to populate the context
when a template is rendered with a request'''
from django.conf import settings


def cdn(request):
    ''' Add available CDNs. '''
    return {'CDN': settings.CDN}
