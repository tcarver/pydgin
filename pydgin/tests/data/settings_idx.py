''' Settings used for the test indices. '''
import os
from elastic.elastic_settings import ElasticSettings
import json
import requests
from elastic.search import Search
from django.core.management import call_command
import core
from gene.document import GeneDocument
from disease.document import DiseaseDocument
from marker.document import MarkerDocument
from region.document import RegionDocument


class PydginTestSettings(object):
    SEARCH_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    SEARCH_TEST_DATA_PATH = os.path.join(SEARCH_BASE_DIR, 'data/')
    SEARCH_SUFFIX = ElasticSettings.getattr('TEST') + '__pydgin'
    if SEARCH_SUFFIX is None:
        SEARCH_SUFFIX = "test"

    NUMBER_OF_SHARDS = 1

    IDX = {
        'GENE': {
            'indexName': 'test__gene_'+SEARCH_SUFFIX,
            'indexType': 'gene',
            'indexJson': SEARCH_TEST_DATA_PATH+'gene.json',
            'shards': NUMBER_OF_SHARDS
        },
        'GENE_INTERACTIONS': {
            'indexName': 'test__gene_'+SEARCH_SUFFIX,
            'indexType': 'gene_interactions_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'gene_interactions.json',
            'shards': NUMBER_OF_SHARDS
        },
        'GENE_PATHWAY': {
            'indexName': 'test__gene_'+SEARCH_SUFFIX,
            'indexType': 'pathway_genesets',
            'indexJson': SEARCH_TEST_DATA_PATH+'gene_pathway.json',
            'shards': NUMBER_OF_SHARDS
        },
        'STUDY_HITS': {
            'indexName': 'test__region_'+SEARCH_SUFFIX,
            'indexType': 'study_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'study_hits.json',
            'shards': NUMBER_OF_SHARDS
        },
        'REGION': {
            'indexName': 'test__region_'+SEARCH_SUFFIX,
            'indexType': 'region_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'region.json',
            'shards': NUMBER_OF_SHARDS
        },
        'DISEASE_LOCUS': {
            'indexName': 'test__region_'+SEARCH_SUFFIX,
            'indexType': 'disease_locus_test',
            'indexJson': SEARCH_TEST_DATA_PATH+'disease_locus.json',
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

    OVERRIDE_SETTINGS = {
        'default': {
            'ELASTIC_URL': [ElasticSettings.url()],
            'DOCUMENT_FACTORY': core.document.PydginDocument.factory,
            'IDX': {
                'GENE': {
                    'name': IDX['GENE']['indexName'],
                    'idx_type': {
                        'GENE': {'type': IDX['GENE']['indexType'], 'search': True,
                                 'auth_public': True, 'class': GeneDocument},
                        'PATHWAY': {'type': 'pathway_genesets', 'auth_public': True},
                        'INTERACTIONS': {'type': IDX['GENE_INTERACTIONS']['indexType'],  'auth_public': True}
                    },
                    'suggester': True, 'auth_public': True
                },
                'PUBLICATION': {
                    'name': IDX['PUBLICATION']['indexName'],
                    'idx_type': {
                        'PUBLICATION': {'type': IDX['PUBLICATION']['indexType'], 'search': True,  'auth_public': True}
                    },
                    'suggester': True, 'auth_public': True
                },
                'DISEASE': {
                    'name': IDX['DISEASE']['indexName'],
                    'idx_type': {
                        'DISEASE': {'type': IDX['DISEASE']['indexType'], 'search': True,
                                    'auth_public': True, 'class': DiseaseDocument}
                    },
                    'suggester': True, 'auth_public': True
                },
                'MARKER': {
                    'name': IDX['MARKER']['indexName'], 'build': '38',
                    'idx_type': {
                        'MARKER': {'type': IDX['MARKER']['indexType'], 'search': True,
                                   'auth_public': True, 'class': MarkerDocument}
                    },
                    'suggester': True,
                    'auth_public': True
                },
                'REGION': {
                   'name': IDX['STUDY_HITS']['indexName'],
                   'idx_type': {
                        'STUDY_HITS': {'type': IDX['STUDY_HITS']['indexType'], 'search': True,  'auth_public': True},
                        'DISEASE_LOCUS': {'type': IDX['DISEASE_LOCUS']['indexType'],  'auth_public': True},
                        'REGION': {'type': IDX['REGION']['indexType'], 'search': True,
                                   'auth_public': True, 'class': RegionDocument}
                    },
                   'auth_public': True
                }
            }
        }
    }

    @classmethod
    def setupIdx(cls, idx_name_arr):
        ''' Setup indices in the given array of key names (e.g. ['GENE', 'DIISEASE', ...]). '''
        idx_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "full_name": {"filter": ["standard", "lowercase"], "tokenizer": "keyword"}}
                },
                "number_of_shards": 1
            }
        }
        IDX = PydginTestSettings.IDX
        for name in idx_name_arr:
            requests.put(ElasticSettings.url() + '/' + IDX[name]['indexName'], data=json.dumps(idx_settings))
            call_command('index_search', **IDX[name])
        for name in idx_name_arr:
            # wait for the elastic load to finish
            Search.index_refresh(IDX[name]['indexName'])

    @classmethod
    def tearDownIdx(cls, idx_name_arr):
        ''' Remove indices by their key names (e.g. ['GENE', 'DIISEASE', ...]). '''
        for name in idx_name_arr:
            requests.delete(ElasticSettings.url() + '/' + PydginTestSettings.IDX[name]['indexName'])
