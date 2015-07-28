''' Pydgin global tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings
import requests


class PydginTest(TestCase):

    def test_url(self):
        ''' Test the search page. '''
        url = reverse('search_page')
        self.assertEqual(url, '/search/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_settings(self):
        ''' Test elastic server is running. '''
        resp = requests.get(ElasticSettings.url())
        self.assertEqual(resp.status_code, 200)
