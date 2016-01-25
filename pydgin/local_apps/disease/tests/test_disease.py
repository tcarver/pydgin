''' Data integrity tests for disease index '''
from django.test import TestCase
from elastic.elastic_settings import ElasticSettings
import logging
from disease import utils

logger = logging.getLogger(__name__)


class DiseaseTest(TestCase):
    idx = ''

    @classmethod
    def setUpClass(cls):
        DiseaseTest.idx = ElasticSettings.idx('DISEASE')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_all_diseases(self):
        ''' Test gteting all diseases on the site '''
        (main, other) = utils.Disease.get_site_diseases()
        self.assertEqual(12, len(main), "12 main diseases found when searching for all diseases")
        self.assertEqual(7, len(other), "7 other diseases found when searching for all diseases")

    def test_main_diseases(self):
        ''' Test gteting all diseases on the site '''
        (main, other) = utils.Disease.get_site_diseases(tier=0)
        self.assertEqual(12, len(main), "12 main diseases found when searching for main diseases")
        self.assertEqual(0, len(other), "0 other diseases found when searching for main diseases")

    def test_other_diseases(self):
        ''' Test gteting all diseases on the site '''
        (main, other) = utils.Disease.get_site_diseases(tier=1)
        self.assertEqual(0, len(main), "12 main diseases found when searching for other diseases")
        self.assertEqual(7, len(other), "0 other diseases found when searching for other diseases")
