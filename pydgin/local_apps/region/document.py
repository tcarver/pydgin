'''
Created on 26 Jan 2016

@author: ellen
'''
import locale

from criteria.helper.criteria import Criteria
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings

from core.document import FeatureDocument, PydginDocument
from pydgin import pydgin_settings
from elastic.aggs import Agg, Aggs
from elastic.query import Query, BoolQuery, Filter
from elastic.search import ElasticQuery, Search
from elastic.result import Document


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
            diseases = [getattr(d, "code") for d in Criteria.get_disease_tags(getattr(self, "region_id"),
                                                                              idx=ElasticSettings.idx('REGION_CRITERIA'))]
            return diseases
            # return getattr(self, "tags")['disease']
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


class DiseaseLocusDocument(PydginDocument):

    @classmethod
    def get_disease_loci_docs(cls, disease):
        ''' Get sorted list of DiseaseLocusDocument's. '''
        query = ElasticQuery(Query.term("disease", disease.lower()))
        disease_loci_docs = Search(query, idx=ElasticSettings.idx('REGION', 'DISEASE_LOCUS'), size=500).search().docs
        return Document.sorted_alphanum(disease_loci_docs, 'seqid')

    def get_disease_region(self):
        ''' Get the disease region object by combining the hits. '''
        locus_start = Agg('region_start', 'min', {'field': 'build_info.start'})
        locus_end = Agg('region_end', 'max', {'field': 'build_info.end'})
        match_agg = Agg('filtered_result', 'filter', Query.match("build_info.build",
                        pydgin_settings.DEFAULT_BUILD).query_wrap(),
                        sub_agg=[locus_start, locus_end])
        build_info_agg = Agg('build_info', 'nested', {"path": 'build_info'}, sub_agg=[match_agg])
        hits = getattr(self, "hits")
        hits_query = ElasticQuery(BoolQuery(must_arr=Query.ids(hits),
                                            b_filter=Filter(Query.missing_terms("field", "group_name"))))
        hits_res = Search(hits_query, idx=ElasticSettings.idx('REGION', 'STUDY_HITS'),
                          aggs=Aggs(build_info_agg), size=len(hits)).search()
        self.hit_docs = hits_res.docs
        if hits_res.hits_total < 1:
            return None
        build_info = getattr(hits_res.aggs['build_info'], 'filtered_result')
        regions_start = int(build_info['region_start']['value'])
        regions_stop = int(build_info['region_end']['value'])

        ens_cand_genes = []
        for h in self.hit_docs:
            if h.genes is not None:
                ens_cand_genes.extend(h.genes)

        return {
            'region_name': getattr(self, "region_name"),
            'locus_id': getattr(self, "locus_id"),
            'seqid': 'chr'+getattr(self, "seqid"),
            'rstart': regions_start,
            'rstop': regions_stop,
            'start': str(locale.format("%d", regions_start, grouping=True)),
            'end': str(locale.format("%d", regions_stop, grouping=True)),
            'all_diseases': [getattr(self, 'disease')],
            'markers': list(set([h.marker for h in self.hit_docs])),
            'ens_cand_genes': ens_cand_genes
        }
