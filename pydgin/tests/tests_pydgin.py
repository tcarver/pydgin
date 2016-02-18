''' Pydgin global tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from elastic.elastic_settings import ElasticSettings
import requests
from builtins import classmethod


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


class PydginTestUtils():

    @classmethod
    def test_links_in_page(cls, test_case, url, data={}):
        resp = test_case.client.get(url, data)
        content = resp.content.decode("utf-8")
        body = content[content.find('<body>'):]

        # remove scripts from body
        parts = body.split('script>')
        i = 0
        txt = ''
        for part in parts:
            if i % 3 == 1:
                txt += part
            i += 1

        data = txt.split("</a>")
        tag = "<a href=\""
        endtag = "\""
        for item in data:
            if "<a href" in item:
                try:
                    ind = item.index(tag)
                    item = item[ind+len(tag):]
                    end = item.index(endtag)
                except:
                    pass
                else:
                    path = item[:end]
                    if path == '#':
                        continue
                    elif path.startswith('/') or path.startswith('http') or path.startswith(url):
                        link_url = path
                    else:
                        link_url = url + path
                    if link_url.startswith('http'):
                        resp = requests.get(link_url)
                    else:
                        print(link_url)
                        resp = test_case.client.get(link_url)
                    test_case.assertEqual(resp.status_code, 200, msg=link_url)
