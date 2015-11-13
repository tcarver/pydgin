''' Gene page tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from pydgin.tests.tests_pydgin import PydginTestUtils
from gene import views
from django.http.request import HttpRequest
import json


class GenePageTest(TestCase):

    def test_url(self):
        ''' Test the gene page 404. '''
        url = reverse('gene_page')
        self.assertEqual(url, '/gene/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the gene page 404. '''
        url = reverse('gene_page')
        resp = self.client.get(url, {'g': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_ens_id(self):
        ''' Test the gene page. '''
        url = reverse('gene_page')
        resp = self.client.get(url, {'g': 'ENSG00000134242'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'PTPN22', resp.content)
        self.assertIn(b'protein_coding', resp.content)
        self.assertIn(b'LYP', resp.content)
        self.assertIn(b'26191', resp.content)
        self.assertContains(resp, '<title>ENSG00000134242</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('gene_page'), data={'g': 'ENSG00000134242'})

    def test_pub_details(self):
        ''' Test the pub details JSON response. '''
        req = HttpRequest()
        req.POST['pmids[]'] = '19923204'
        json_resp = views.pub_details(req)
        pmids = json.loads(json_resp.content.decode("utf-8"))['hits']
        self.assertEquals(len(pmids), 1)
        self.assertEquals(pmids[0]['_source']['pmid'], '19923204')
