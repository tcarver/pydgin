''' Test for feature locations rest interface. '''
import json

from django.core.urlresolvers import reverse, NoReverseMatch
from django.test import TestCase


class LocationsRestTest(TestCase):

    def test_ld_list(self):
        ''' Test retrieving markers in LD of given marker. '''
        try:
            url = reverse('rest:locations-list')
            response = self.client.get(url, data={'feature': 'rs2476601', 'build': 'hg38'})
            loc = json.loads(response.content.decode("utf-8"))[0]
            self.assertGreater(len(loc), 0, 'results found')

            response = self.client.get(url, data={'feature': 'PTPN22', 'build': 'hg38'})
            loc = json.loads(response.content.decode("utf-8"))[0]
            self.assertGreater(len(loc), 0, 'results found')

            response = self.client.get(url, data={'feature': '1p13.2', 'build': 'hg38'})
            loc = json.loads(response.content.decode("utf-8"))[0]
            self.assertGreater(len(loc), 0, 'results found')
        except (KeyError, NoReverseMatch):
            pass
