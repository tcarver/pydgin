''' Marker page tests. '''
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from pydgin.tests.data.settings_idx import PydginTestSettings


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' Load test indices (marker) '''
    PydginTestSettings.setupIdx(['MARKER', 'MARKER_IC', 'DISEASE',
                                 'MARKER_CRITERIA_IS_MARKER_IN_MHC', 'MARKER_CRITERIA_IS_AN_INDEX_SNP',
                                 'MARKER_CRITERIA_MARKER_IS_GWAS_SIGNIFICANT_STUDY',
                                 'MARKER_CRITERIA_RSQ_WITH_INDEX_SNP'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['MARKER', 'DISEASE',
                                    'MARKER_CRITERIA_IS_MARKER_IN_MHC', 'MARKER_CRITERIA_IS_AN_INDEX_SNP',
                                    'MARKER_CRITERIA_MARKER_IS_GWAS_SIGNIFICANT_STUDY',
                                    'MARKER_CRITERIA_RSQ_WITH_INDEX_SNP'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class MarkerPageTest(TestCase):

    def test_url(self):
        ''' Test the marker page 404. '''
        url = reverse('marker_page_params')
        self.assertEqual(url, '/marker/')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_url2(self):
        ''' Test the marker page 404. '''
        url = reverse('marker_page_params')
        resp = self.client.get(url, {'m': 'ABC'})
        self.assertEqual(resp.status_code, 404)

    def test_url_rs_id(self):
        ''' Test the marker page. '''
        url = reverse('marker_page_params')
        resp = self.client.get(url, {'m': 'rs2476601'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'rs2476601', resp.content)
        self.assertIn(b'imm_1_114179091', resp.content)
