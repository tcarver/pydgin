'''
Created on 26 Jan 2016

@author: ellen
'''
from core.document import FeatureDocument
import locale
from django.core.urlresolvers import reverse


class RegionDocument(FeatureDocument):
    ''' An extension of a FetaureDocument for a Region. '''
    EXCLUDED_RESULT_KEYS = ['hits', 'pmids', 'disease_loci', 'region_id', 'region_name',
                            'tier', 'species', 'seqid', 'build_info', 'studies']

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

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        if getattr(self, 'build_info') is not None:
            bi = getattr(self, 'build_info')
            location = 'chr' + bi['seqid'] + ':' + str(bi['start']) + '-' + str(bi['end'])
            setattr(self, 'location', location)

        ''' show genes and marker highlights '''
        if self.highlight() is not None:
            new_highlight = {}
            for k, matches in self.highlight().items():
                if k != 'marker' and k != 'genes':
                    continue
                att_key = 'genes' if k == 'genes' else 'markers'
                features = getattr(self, att_key)
                for m in matches:
                    match = m.replace('<strong>', '').replace('</strong>', '')
                    features = [feat if feat != match else m for feat in getattr(self, att_key)]
                new_highlight[att_key] = ['; '.join(features)]

            if new_highlight:
                self.__dict__['_meta']['highlight'] = new_highlight


class StudyHitDocument(FeatureDocument):
    ''' An extension of a FetaureDocument for a Study Hit. '''

    def get_name(self):
        return getattr(self, "chr_band")
