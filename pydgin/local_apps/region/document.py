'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument, PydginDocument
import locale
from django.core.urlresolvers import reverse
from pydgin import pydgin_settings


class RegionDocument(FeatureDocument):
    ''' An extension of a FetaureDocument for a Region. '''
    EXCLUDED_RESULT_KEYS = ['hits', 'pmids', 'disease_loci', 'region_id', 'region_name',
                            'tier', 'species', 'seqid', 'build_info', 'studies', 'tags']

    def get_name(self):
        ''' Override get document name. '''
        return getattr(self, "region_name")

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "region_id")

    def url(self):
        ''' Document page. '''
        return reverse('region_page_params') + '?r='

    def get_position(self, build=pydgin_settings.DEFAULT_BUILD):
        build_info = getattr(self, "build_info")
        if build_info['build'] == build:
            return ("chr" + build_info['seqid'] + ":" + str(locale.format("%d", build_info['start'], grouping=True)) +
                    "-" + str(locale.format("%d", build_info['end'], grouping=True)))
        else:
            return None

    def get_sub_heading(self):
        ''' Overridden get feature sub-heading. '''
        return ""

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        if super(RegionDocument, self).get_diseases():
            return getattr(self, "tags")['disease']
        return []

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        okeys = ['genes', 'markers', 'location']
        for key in keys:
            if key not in okeys:
                okeys.append(key)
        return okeys

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        if getattr(self, 'build_info') is not None:
            setattr(self, 'location', self.get_position())

        ''' show genes and marker highlights '''
        if self.highlight() is not None:
            new_highlight = {}
            for k, matches in self.highlight().items():
                if k != 'marker' and k != 'genes':
                    continue
                attr_key = 'genes' if k == 'genes' else 'markers'
                features = getattr(self, attr_key)
                for m in matches:
                    match = m.replace('<strong>', '').replace('</strong>', '')
                    features = [feat if feat != match else m for feat in getattr(self, attr_key)]
                new_highlight[attr_key] = ['; '.join(features)]

            if new_highlight:
                self.__dict__['_meta']['highlight'] = new_highlight


class StudyHitDocument(PydginDocument):
    ''' An extension of a FeatureDocument for a Study Hit. '''

    def get_name(self):
        return getattr(self, "chr_band")
