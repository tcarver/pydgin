'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument
import locale


class RegionDocument(FeatureDocument):
    '''
    classdocs
    '''

    def get_name(self):
        return getattr(self, "region_name")

    def get_position(self, build=38):
        build_info = getattr(self, "build_info")
        if build_info['build'] == build:
            return "chr" + build_info['seqid'] + ":" + str(locale.format("%d", build_info['start'], grouping=True)) + ".." + str(locale.format("%d", build_info['end'], grouping=True))
        else:
            return None
