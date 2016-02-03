'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument
import locale
from django.core.urlresolvers import reverse


class RegionDocument(FeatureDocument):
    ''' An extension of a FetaureDocument for a Region. '''
    EXCLUDED_KEYS = ['hits']

    def get_name(self):
        ''' Override get document name. '''
        return getattr(self, "region_name")

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "region_id")

    def url(self):
        ''' Document page. '''
        return reverse('region_page_params') + '?r='

    def get_position(self, build=38):
        build_info = getattr(self, "build_info")
        if build_info['build'] == build:
            return ("chr" + build_info['seqid'] + ":" + str(locale.format("%d", build_info['start'], grouping=True)) +
                    ".." + str(locale.format("%d", build_info['end'], grouping=True)))
        else:
            return None


class StudyHitDocument(FeatureDocument):
    ''' An extension of a FetaureDocument for a Study Hit. '''

    def get_name(self):
        return getattr(self, "chr_band")
