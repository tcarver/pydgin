'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import PydginDocument


class StudyDocument(PydginDocument):
    '''
    classdocs
    '''

    def get_name(self):
        return getattr(self, "study_id")

    def get_sub_heading(self):
        return getattr(self, "study_name")
