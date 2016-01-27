''' Pydgin core application tests. '''
from django.test import TestCase
from django.test.utils import override_settings
from pydgin.tests.data.settings_idx import PydginTestSettings
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from gene.document import GeneDocument
from disease.document import DiseaseDocument


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE', 'DISEASE'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'DISEASE'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class FeatureDocumentTest(TestCase):

    def test_doc(self):
        ''' Test return correct type of FeatureDocument. '''
        idx = PydginTestSettings.IDX['GENE']['indexName']
        idx_type = PydginTestSettings.IDX['GENE']['indexType']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['symbol']),
                     idx=idx, idx_type=idx_type, size=2).search()
        docs = res.docs
        for doc in docs:
            self.assertTrue(isinstance(doc, GeneDocument))

    def test_doc2(self):
        ''' Test return correct type of FeatureDocument using multiple index search. '''
        idx = PydginTestSettings.IDX['GENE']['indexName'] + ',' + PydginTestSettings.IDX['DISEASE']['indexName']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['symbol', 'code']),
                     idx=idx, size=40).search()
        docs = res.docs
        for doc in docs:
            self.assertTrue(isinstance(doc, GeneDocument) or isinstance(doc, DiseaseDocument))
            if isinstance(doc, DiseaseDocument):
                self.assertTrue(hasattr(doc, 'code'))
