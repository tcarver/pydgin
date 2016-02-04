'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import PydginDocument
from django.core.urlresolvers import reverse


class StudyDocument(PydginDocument):
    ''' Study document object. '''

    def get_name(self):
        return getattr(self, "study_id")

    def get_sub_heading(self):
        return getattr(self, "study_name")

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        ''' Document page link. '''
        return reverse('study_page_params') + '?s='
