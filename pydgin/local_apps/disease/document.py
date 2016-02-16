'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument
from django.core.urlresolvers import reverse


class DiseaseDocument(FeatureDocument):
    ''' Disease document.'''

    def get_name(self):
        return getattr(self, "name")

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "code")

    def url(self):
        return reverse('disease_page_params')
