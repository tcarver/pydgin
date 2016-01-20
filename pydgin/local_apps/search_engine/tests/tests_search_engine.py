''' Pydgin Search Engine tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.management import call_command
import json
from pydgin.tests.tests_pydgin import PydginTestUtils

from elastic.elastic_settings import ElasticSettings
from django.test.utils import override_settings
from pydgin.tests.data.settings_idx import IDX
import requests
from elastic.search import Search, ElasticQuery, Update
from elastic.query import Query

OVERRIDE_SETTINGS = {
    'default': {
        'ELASTIC_URL': [ElasticSettings.url()],
        'IDX': {
            'GENE': {
                'name': IDX['GENE']['indexName'],
                'idx_type': {'GENE': {'type': IDX['GENE']['indexType'], 'search': True,  'auth_public': True}},
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
                    'DISEASE': {'type': IDX['DISEASE']['indexType'], 'search': True,  'auth_public': True}
                },
                'suggester': True, 'auth_public': True
            },
            'MARKER': {
                'name': IDX['MARKER']['indexName'], 'build': '38',
                'idx_type': {
                    'MARKER': {'type': IDX['MARKER']['indexType'], 'search': True,  'auth_public': True}
                },
                'suggester': True,
                'auth_public': True
            },
            'REGION': {
               'name': IDX['STUDY_HITS']['indexName'],
               'idx_type': {
                    'STUDY_HITS': {'type': IDX['STUDY_HITS']['indexType'], 'search': True,  'auth_public': True}
                },
               'auth_public': True
            }
        }
    }
}


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    idx_settings = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "full_name": {"filter": ["standard", "lowercase"], "tokenizer": "keyword"}}
            }
        }
    }

    requests.put(ElasticSettings.url() + '/' + IDX['GENE']['indexName'], data=json.dumps(idx_settings))
    requests.put(ElasticSettings.url() + '/' + IDX['STUDY_HITS']['indexName'], data=json.dumps(idx_settings))
    requests.put(ElasticSettings.url() + '/' + IDX['DISEASE']['indexName'], data=json.dumps(idx_settings))
    requests.put(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'], data=json.dumps(idx_settings))
    call_command('index_search', **IDX['GENE'])
    call_command('index_search', **IDX['STUDY_HITS'])
    call_command('index_search', **IDX['PUBLICATION'])
    call_command('index_search', **IDX['DISEASE'])
    call_command('index_search', **IDX['MARKER'])

    # wait for the elastic load to finish
    Search.index_refresh(IDX['GENE']['indexName'])
    Search.index_refresh(IDX['STUDY_HITS']['indexName'])
    Search.index_refresh(IDX['PUBLICATION']['indexName'])
    Search.index_refresh(IDX['DISEASE']['indexName'])
    Search.index_refresh(IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['GENE']['indexName'])
    requests.delete(ElasticSettings.url() + '/' + IDX['STUDY_HITS']['indexName'])
    requests.delete(ElasticSettings.url() + '/' + IDX['PUBLICATION']['indexName'])
    requests.delete(ElasticSettings.url() + '/' + IDX['DISEASE']['indexName'])
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class AuthSearchEngineTest(TestCase):

    def test_doc_auth(self):
        idx = IDX['STUDY_HITS']['indexName']
        docs = Search(ElasticQuery(Query.match_all(), sources=['chr_band', 'marker']), idx=idx, size=1).search().docs
        self.assertEquals(len(docs), 1, "STUDY_HITS document")
        marker_id = getattr(docs[0], 'marker')

        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query='+marker_id)
        nhits1 = resp.context['hits_total']
        self.assertGreater(nhits1, 0, 'search hits > 0')
        # update document to be in DIL
        update_field = {"doc": {"group_name": "DIL"}}
        Update.update_doc(docs[0], update_field)
        Search.index_refresh(IDX['STUDY_HITS']['indexName'])

        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query='+marker_id)
        nhits2 = resp.context['hits_total']
        self.assertEqual(nhits1-1, nhits2, 'private document hidden')


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class SearchEngineTest(TestCase):

    def test_search_page(self):
        ''' Test the search page. '''
        url = reverse('search_page')
        self.assertEqual(url, '/search/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'search_engine/search.html')

    def test_search(self):
        ''' Test the search. '''
        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query=%2BPTPN22+%2Btodd')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "+PTPN22 +todd")
        self.assertGreater(resp.context['hits_total'], 0)
        self.assertTemplateUsed(resp, 'search_engine/result.html')

    def test_search2(self):
        ''' Test the search on specified fields in the index. '''
        url = reverse('search_page')
        resp = self.client.post(url+'?idx=ALL&query=%2jouhn+%2Btodd+%2Bt1d',
                                {"publication_tags_disease": "publication:tags:disease",
                                 "publication_authors_name": "publication:authors:name"})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 0)

    def test_search3(self):
        ''' Test the search specifying the field in the query. '''
        url = reverse('search_page')
        resp = self.client.get(url+'?idx=ALL&query=dbxrefs.swissprot:Q9Y2R2')
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 0)

    def test_search_filters(self):
        ''' Test the search with filters applied. '''
        url = "%s?idx=GENE&query=PTPN2*" % reverse('search_page')
        resp = self.client.post(url, data={"biotypes": "protein_coding", "saved-biotypes": "antisense",
                                           "saved-biotypes": "antisense"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "PTPN2*")
        self.assertGreaterEqual(resp.context['hits_total'], 1)
        self.assertTemplateUsed(resp, 'search_engine/result.html')
        biotypes = resp.context['aggs']['biotypes'].get_buckets()
        self.assertEqual(len(biotypes), 2)
        if biotypes[0]['key'] == 'protein_coding':
            protein_coding = biotypes[0]
            antisense = biotypes[1]
        else:
            protein_coding = biotypes[1]
            antisense = biotypes[0]
        self.assertGreater(protein_coding['doc_count'], 0)
        self.assertEquals(antisense['doc_count'], 0)

    def test_search_filters2(self):
        ''' Test applying categories filter. Query first without filter and then
        with to get just the gene. '''
        url = "%s?idx=ALL&query=PTPN12" % reverse('search_page')
        data = {
            'categories': 'gene',
            'categories': 'publication',
            'biotypes': 'protein_coding',
            'gene_symbol': 'gene:symbol',
            'publication_title': 'publication:title'
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)
        nhits1 = resp.context['hits_total']
        self.assertGreater(nhits1, 1)

        del data['publication_title']
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 200)
        nhits2 = resp.context['hits_total']
        self.assertEqual(nhits2, 1)
        self.assertGreater(nhits1, nhits2)

    def test_search_filters3(self):
        ''' Test filtering the gene biotype as well as other index types. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "PTPN12",
                                     "categories": "gene", "categories": "publication",
                                     "biotypes": "protein_coding"})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['hits_total'], 1)

    def test_suggester(self):
        ''' Test the auto suggester for searches. '''
        url = reverse('suggester')
        resp = self.client.get(url, {"idx": "ALL", "term": "PT"})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf-8'))
        self.assertTrue('PTPN22' in data['data'])


class HyperLinksTest(TestCase):
    ''' Hyperlinks on live site. '''

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('search_page'))
