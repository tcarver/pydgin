''' Test for disease region rest interface. '''
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings
from pydgin.tests.data.settings_idx import PydginTestSettings


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE', 'MARKER', 'STUDY_HITS', 'DISEASE_LOCUS', 'REGION', 'DISEASE', 'IC_STATS'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'MARKER', 'STUDY_HITS', 'DISEASE_LOCUS', 'REGION', 'DISEASE', 'IC_STATS'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class LocationsRestTest(TestCase):

    def test_regions_list(self):
        ''' Test retrieving regions, genes and markers in disease regions. '''
        url = reverse('rest:regions-list')
        response = self.client.get(url, data={'disease': 'T1D', 'build': 'hg38'})
        reg = json.loads(response.content.decode("utf-8"))
        self.assertGreater(len(reg), 0, 'results found')

        # test getting genes in region
        response = self.client.get(url, data={'disease': 'T1D', 'build': 'hg38', 'genes': 'true', 'regions': 'false'})
        reg = json.loads(response.content.decode("utf-8"))
        self.assertGreater(len(reg), 0, 'results found')

        # test getting markers in region
        response = self.client.get(url, data={'disease': 'T1D', 'build': 'hg38', 'markers': 'true', 'regions': 'false'})
        reg = json.loads(response.content.decode("utf-8"))
        self.assertGreater(len(reg), 0, 'results found')
