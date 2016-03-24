'''
Created on 26 Jan 2016

@author: ellen
'''
from criteria.helper.criteria import Criteria
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings

from core.document import PydginDocument


class StudyDocument(PydginDocument):
    ''' Study document object. '''
    EXCLUDED_RESULT_KEYS = ['study_id', 'description']

    def get_name(self):
        return getattr(self, "study_id")

    def get_sub_heading(self):
        return getattr(self, "study_name")

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        if super(StudyDocument, self).get_diseases():
            diseases = [getattr(d, "code") for d in Criteria.get_disease_tags(self.get_name(),
                                                                              idx=ElasticSettings.idx('STUDY_CRITERIA'))]
            return diseases
        return []

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        ''' Document page link. '''
        return reverse('study_page_params') + '?s='
