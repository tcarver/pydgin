''' Pydgin Search Engine tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse


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
        resp = self.client.get(url, {"idx": "ALL", "query": "+PTPN22 +todd"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "+PTPN22 +todd")
        self.assertGreaterEqual(resp.context['hits_total'], 0)
        self.assertTemplateUsed(resp, 'search_engine/result.html')
