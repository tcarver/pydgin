''' Gene page tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse


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
