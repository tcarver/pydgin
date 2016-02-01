''' Gene document. '''
from core.document import FeatureDocument
from django.core.urlresolvers import reverse


class GeneDocument(FeatureDocument):
    ''' Gene document object. '''

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        dbxrefs = getattr(self, 'dbxrefs')
        if dbxrefs is not None:
            dbs = dbxrefs.keys()
            for db in list(dbs):
                if db not in ['ensembl', 'entrez']:
                    del dbxrefs[db]

    def result_card_keys(self):
        ''' Gets the keys of the document object to show in the result card. '''
        keys = super().result_card_keys()
        keys.remove('symbol')
        keys.insert(0, 'symbol')
        return keys

    def get_name(self):
        return getattr(self, "symbol")

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "dbxrefs")['ensembl']

    def url(self):
        ''' Document page. '''
        return reverse('gene_page') + '?g='

    def comparable(self):
        ''' Document(s) can be compared. '''
        return True
