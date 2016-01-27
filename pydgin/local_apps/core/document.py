'''
Created on 26 Jan 2016

@author: ellen
'''
from elastic.result import Document


class FeatureDocument(Document):
    '''
    classdocs
    '''

    def get_name(self):
        ''' Overridden get feature name. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_position(self, build=38):
        '''
        Overridden get feature position by build.
        @type  build: integer
        @keyword build: NCBI build to return (default: 38).
         '''
        raise NotImplementedError("Inheriting class should implement this method")
