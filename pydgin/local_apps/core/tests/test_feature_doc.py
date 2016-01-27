''' Pydgin core application tests. '''
from django.test import TestCase
from django.test.utils import override_settings
from pydgin.tests.data.settings_idx import PydginTestSettings
from elastic.search import ElasticQuery, Search
from elastic.query import Query
from gene.document import GeneDocument
from disease.document import DiseaseDocument
from core.document import PydginDocument


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def setUpModule():
    ''' create elastic indices for querying '''
    PydginTestSettings.setupIdx(['GENE', 'DISEASE', 'PUBLICATION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
def tearDownModule():
    ''' Remove test indices '''
    PydginTestSettings.tearDownIdx(['GENE', 'DISEASE', 'PUBLICATION'])


@override_settings(ELASTIC=PydginTestSettings.OVERRIDE_SETTINGS)
class PydginDocumentTest(TestCase):

    def test_doc(self):
        ''' Test return correct type of FeatureDocument. '''
        idx = PydginTestSettings.IDX['GENE']['indexName']
        idx_type = PydginTestSettings.IDX['GENE']['indexType']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['symbol']),
                     idx=idx, idx_type=idx_type, size=2).search()
        for doc in res.docs:
            self.assertTrue(isinstance(doc, GeneDocument))

    def test_doc2(self):
        ''' Test return correct type of FeatureDocument using multiple index search. '''
        idx = PydginTestSettings.IDX['GENE']['indexName'] + ',' + PydginTestSettings.IDX['DISEASE']['indexName']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['symbol', 'code']),
                     idx=idx, size=40).search()
        for doc in res.docs:
            self.assertTrue(isinstance(doc, GeneDocument) or isinstance(doc, DiseaseDocument))
            if isinstance(doc, DiseaseDocument):
                self.assertTrue(hasattr(doc, 'code'))

    def test_doc3(self):
        ''' Test return correct type of PydginDocument/FeatureDocument using multiple index search. '''
        idx = PydginTestSettings.IDX['DISEASE']['indexName'] + ',' + PydginTestSettings.IDX['PUBLICATION']['indexName']
        res = Search(search_query=ElasticQuery(Query.match_all(), sources=['code', 'pmid']),
                     idx=idx, size=40).search()

        for doc in res.docs:
            self.assertTrue(isinstance(doc, PydginDocument) or isinstance(doc, DiseaseDocument))
            if isinstance(doc, PydginDocument):
                self.assertTrue(hasattr(doc, 'pmid'))
            else:
                self.assertTrue(hasattr(doc, 'code'))
