'''
Created on 15 Jan 2016

@author: ellen

Utility functions for Regions.
'''

import logging
from elastic.elastic_settings import ElasticSettings
from elastic.search import Search, ElasticQuery
from elastic.query import Query

logger = logging.getLogger(__name__)


class Region(object):
    '''
    Region class to define functions for changing between regions/disease loci/hits in index.
    '''

    @classmethod
    def hits_to_regions(cls, docs):
        ''' Returns the region docs for given hit docs '''
        idx = ElasticSettings.idx('REGION', 'REGION')
        disease_loci = [getattr(doc, "disease_locus").lower() for doc in docs]
        results = Search(search_query=ElasticQuery(Query.terms("disease_loci", disease_loci)),
                         idx=idx).search()
        return results.docs
