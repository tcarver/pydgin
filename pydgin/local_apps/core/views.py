''' Core view class mixins. '''
from django.conf import settings


class SectionMixin(object):
    ''' Adds sections to the view context. '''

    def get_context_data(self, **kwargs):
        context = super(SectionMixin, self).get_context_data(**kwargs)
        context['sections'] = [k for k, v in settings.PAGE_SECTIONS[self.__class__.__name__].items() if v]
        return context
