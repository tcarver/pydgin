''' Gene document. '''
from core.document import FeatureDocument
from django.core.urlresolvers import reverse


class GeneDocument(FeatureDocument):
    ''' Gene document object. '''

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
