'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument


class MarkerDocument(FeatureDocument):
    '''
    classdocs
    '''

    def get_name(self):
        print(self.__dict__)
        return getattr(self, "id")
