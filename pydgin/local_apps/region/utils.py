'''
Created on 15 Jan 2016

@author: ellen

Utility functions for Regions.
'''

import logging
from elastic.elastic_settings import ElasticSettings
from elastic.search import Search, ElasticQuery
from elastic.query import Query, FilteredQuery, BoolQuery, Filter
from elastic.aggs import Agg, Aggs

logger = logging.getLogger(__name__)


class Region(object):
    '''
    Region class to define functions for changing between regions/disease loci/hits in index.
    '''

    @classmethod
    def hits_to_regions(cls, docs):
        ''' Returns the region docs for given hit docs '''
        hits_idx = ElasticSettings.idx('REGION', 'REGION')
        disease_loci = [getattr(doc, "disease_locus").lower() for doc in docs]
        resultObj = Search(search_query=ElasticQuery(Query.terms("disease_loci", disease_loci)),
                         idx=hits_idx).search()
        return resultObj.docs

    @classmethod
    def pad_region_doc(cls, region):
        '''Adds details of disease_loci & hits for a given region doc'''
        hits_idx = ElasticSettings.idx('REGION', 'STUDY_HITS')

        disease_loci = getattr(region, "disease_loci")

        locus_start = Agg('region_start', 'min', {'field': 'build_info.start'})
        locus_end = Agg('region_end', 'max', {'field': 'build_info.end'})
        match_agg = Agg('filtered_result', 'filter', Query.match("build_info.build", 38).query_wrap(),
                        sub_agg=[locus_start, locus_end])
        build_info_agg = Agg('build_info', 'nested', {"path": 'build_info'}, sub_agg=[match_agg])

        query = ElasticQuery(FilteredQuery(Query.terms("disease_locus", disease_loci),
                                           Filter(BoolQuery(should_arr=[Query.missing_terms("field", "group_name")]
                                                            ))))
        resultObj = Search(search_query=query, idx=hits_idx, aggs=Aggs(build_info_agg)).search()
        build_info = getattr(resultObj.aggs['build_info'], 'filtered_result')
        region_start = int(build_info['region_start']['value'])
        region_end = int(build_info['region_end']['value'])

        setattr(region, "start", region_start)
        setattr(region, "end", region_end)

        return region
