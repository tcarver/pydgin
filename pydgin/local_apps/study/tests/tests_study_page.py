''' Gene page tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse
from pydgin.tests.tests_pydgin import PydginTestUtils


class StudyPageTest(TestCase):

    def test_url(self):
        ''' Test the region page 404. '''
        url = reverse('study_page_params')
        self.assertEqual(url, '/study/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the study page 404. '''
        url = reverse('study_page_params')
        resp = self.client.get(url, {'s': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_region_id(self):
        ''' Test the study page. '''
        url = reverse('study_page_params')
        resp = self.client.get(url, {'s': 'GDXHsS00004'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'GDXHsS00004', resp.content)
        self.assertContains(resp, '<title>Whole Genome Association Study:T1D:Barrett JC:Nat Genet:2009:19430480</title>')

    def test_hyperlinks(self):
        ''' Test example hyperlinks. '''
        PydginTestUtils.test_links_in_page(self, reverse('study_page_params'), data={'s': 'GDXHsS00004'})
