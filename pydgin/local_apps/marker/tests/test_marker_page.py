''' Gene page tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from elastic.tests.settings_idx import OVERRIDE_SETTINGS, IDX
from django.core.management import call_command
from elastic.search import Search
from elastic.elastic_settings import ElasticSettings
import requests


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    call_command('index_search', **IDX['MARKER'])
    call_command('index_search', **IDX['MARKER_RS_HISTORY'])
    call_command('index_search', **IDX['JSON_MARKER_IC'])
    Search.index_refresh(IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    requests.delete(ElasticSettings.url() + '/' + IDX['MARKER']['indexName'])


@override_settings(ELASTIC=OVERRIDE_SETTINGS)
class MarkerPageTest(TestCase):

    def test_url(self):
        ''' Test the gene page 404. '''
        url = reverse('marker_page')
        self.assertEqual(url, '/marker/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the gene page 404. '''
        url = reverse('marker_page')
        resp = self.client.get(url, {'m': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_rs_id(self):
        ''' Test the gene page. '''
        url = reverse('marker_page')
        resp = self.client.get(url, {'m': 'rs2476601'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'rs2476601', resp.content)
        self.assertIn(b'imm_1_114179091', resp.content)
