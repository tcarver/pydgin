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
