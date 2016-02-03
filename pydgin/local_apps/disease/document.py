'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument


class DiseaseDocument(FeatureDocument):
    '''
    classdocs
    '''

    def get_name(self):
        return getattr(self, "name")

    def get_sub_heading(self):
        ''' Overridden get feature sub-heading. '''
        return ""

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        return [getattr(self, "code")]
