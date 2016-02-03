'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument
from django.core.urlresolvers import reverse


class StudyDocument(FeatureDocument):
    ''' Study document object. '''
    EXCLUDED_KEYS = ['study_id']

    def get_name(self):
        return getattr(self, "study_id")

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        ''' Document page link. '''
        return reverse('study_page_params') + '?s='
