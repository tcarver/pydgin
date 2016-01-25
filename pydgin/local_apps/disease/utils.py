'''
Created on 25 Jan 2016

@author: ellen

Utility functions for Regions.
'''

import logging
from elastic.elastic_settings import ElasticSettings
from elastic.search import Search, ElasticQuery, Sort
from elastic.query import Query, FilteredQuery, Filter

logger = logging.getLogger(__name__)


class Disease(object):
    '''
    Disease class to define utility functions for diseases on the site.
    '''

    @classmethod
    def get_site_diseases(cls, tier=None):
        ''' Returns the region docs for given hit docs '''
        idx = ElasticSettings.idx('DISEASE', 'DISEASE')

        query = Query.match_all()
        if tier is not None:
            query = FilteredQuery(Query.match_all(), Filter(Query.term("tier", tier)))

        resultObj = Search(search_query=ElasticQuery(query), idx=idx, qsort=Sort('code:asc')).search()

        main = []
        other = []
        for doc in resultObj.docs:
            if getattr(doc, "tier") == 0:
                main.append(doc)
            elif getattr(doc, "tier") == 1:
                other.append(doc)

        return (main, other)
