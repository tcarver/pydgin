''' Pydgin global tests. '''
from django.test import TestCase
from django.core.urlresolvers import reverse


class PydginTest(TestCase):

    def test_url(self):
        ''' Test the search page. '''
        url = reverse('search_page')
        self.assertEqual(url, '/search/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
