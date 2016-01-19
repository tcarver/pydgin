''' Settings used for the tests. '''
import os
from elastic.elastic_settings import ElasticSettings

SEARCH_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SEARCH_TEST_DATA_PATH = os.path.join(SEARCH_BASE_DIR, 'data/')
SEARCH_SUFFIX = ElasticSettings.getattr('TEST') + '__pydgin'
if SEARCH_SUFFIX is None:
    SEARCH_SUFFIX = "test"

NUMBER_OF_SHARDS = 1

IDX = {
    'GENE': {
        'indexName': 'test__gene_'+SEARCH_SUFFIX,
        'indexType': 'gene_test',
        'indexJson': SEARCH_TEST_DATA_PATH+'gene.json',
        'shards': NUMBER_OF_SHARDS
    },
    'STUDY_HITS': {
        'indexName': 'test__region_'+SEARCH_SUFFIX,
        'indexType': 'study_test',
        'indexJson': SEARCH_TEST_DATA_PATH+'study_hits.json',
        'shards': NUMBER_OF_SHARDS
    },
    'PUBLICATION': {
        'indexName': 'test__pub_'+SEARCH_SUFFIX,
        'indexType': 'publication_test',
        'indexJson': SEARCH_TEST_DATA_PATH+'pub.json',
        'shards': NUMBER_OF_SHARDS
    },
    'DISEASE': {
        'indexName': 'test__disease_'+SEARCH_SUFFIX,
        'indexType': 'disease_test',
        'indexJson': SEARCH_TEST_DATA_PATH+'disease.json',
        'shards': NUMBER_OF_SHARDS
    },
    'MARKER': {
        'indexName': 'test__marker_'+SEARCH_SUFFIX,
        'indexType': 'marker_test',
        'indexJson': SEARCH_TEST_DATA_PATH+'marker.json',
        'shards': NUMBER_OF_SHARDS
    }
}
