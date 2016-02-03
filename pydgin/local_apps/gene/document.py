'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument


class GeneDocument(FeatureDocument):
    '''
    classdocs
    '''

    def get_name(self):
        return getattr(self, "symbol")

    def get_sub_heading(self):
        return getattr(self, "description")

    def get_diseases(self):
        return ['atd', 'cro', 'jia', 'ra', 'sle', 't1d', 'ibd', 'ssc', 'vit']
