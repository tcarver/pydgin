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

    def test_search(self):
        ''' Test the search. '''
        url = reverse('search_page')
        resp = self.client.get(url, {"idx": "ALL", "query": "+PTPN22 +todd"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], "+PTPN22 +todd")
        self.assertGreaterEqual(resp.context['hits_total'], 0)
        self.assertTemplateUsed(resp, 'search_engine/result.html')
