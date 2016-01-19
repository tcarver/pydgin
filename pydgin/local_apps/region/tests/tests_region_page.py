''' Gene page tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from pydgin.tests.tests_pydgin import PydginTestUtils


class RegionPageTest(TestCase):

    def test_url(self):
        ''' Test the gene page 404. '''
        url = reverse('region_page')
        self.assertEqual(url, '/region/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the gene page 404. '''
        url = reverse('region_page')
        resp = self.client.get(url, {'r': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_region_id(self):
        ''' Test the gene page. '''
        url = reverse('region_page')
        resp = self.client.get(url, {'r': '1p13.2_019'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'1p13.2', resp.content)
        self.assertContains(resp, '<title>1p13.2</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('region_page'), data={'r': '1p13.2_019'})
