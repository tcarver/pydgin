''' Pydgin Search Engine tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
import json


class SearchEngineTest(TestCase):

    def test_search_page(self):
        ''' Test the search page. '''
        url = reverse('search_page')
        self.assertEqual(url, '/search/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'search_engine/search.html')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        url = reverse('search_page')
        resp = self.client.get(url)
        data = resp.content.decode("utf-8") .split("</a>")
        tag = "<a href=\""
        endtag = "\">"
        for item in data:
            if "<a href" in item:
                try:
                    ind = item.index(tag)
                    item = item[ind+len(tag):]
                    end = item.index(endtag)
                except:
                    pass
                else:
                    link_url = url + item[:end]
                    resp = self.client.get(link_url)
                    self.assertEqual(resp.status_code, 200, msg=link_url)
                    self.assertGreater(resp.context['hits_total'], 0)

    def test_search(self):
        ''' Test the search. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "+PTPN22 +todd"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "+PTPN22 +todd")
        self.assertGreater(resp.context['hits_total'], 0)
        self.assertTemplateUsed(resp, 'search_engine/result.html')

    def test_search_filters(self):
        ''' Test the search with filters applied. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "PTPN2*", "biotypes": "protein_coding"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "PTPN2*")
        self.assertGreaterEqual(resp.context['hits_total'], 1)
        self.assertTemplateUsed(resp, 'search_engine/result.html')
        biotypes = resp.context['aggs']['biotypes'].get_buckets()
        self.assertEqual(len(biotypes), 1)
        self.assertEqual(biotypes[0]['key'], 'protein_coding')

    def test_search_filters2(self):
        ''' Test applying categories filter. Query first without filter and then
        with to get just the gene. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "PTPN12"})
        self.assertEqual(resp.status_code, 200)
        nhits1 = resp.context['hits_total']
        self.assertGreater(nhits1, 1)
        resp = self.client.get(url, {"idx": "ALL", "query": "PTPN12", "categories": "gene"})
        self.assertEqual(resp.status_code, 200)
        nhits2 = resp.context['hits_total']
        self.assertEqual(nhits2, 1)
        self.assertGreater(nhits1, nhits2)

    def test_suggester(self):
        ''' Test the auto suggester for searches. '''
        url = reverse('suggester')
        resp = self.client.get(url, {"idx": "ALL", "term": "PT"})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf-8'))
        self.assertTrue('PTPN22' in data['data'])
