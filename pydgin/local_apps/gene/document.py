''' Gene document. '''
from core.document import FeatureDocument
from django.core.urlresolvers import reverse


class GeneDocument(FeatureDocument):
    ''' Gene document object. '''
    EXCLUDED_RESULT_KEYS = ['dbxrefs']

    def result_card_process_attrs(self):
        ''' Show only subset of dbxrefs. '''
        dbxrefs = getattr(self, 'dbxrefs')
        dbx = {}
        if 'ensembl' in dbxrefs:
            dbx['Ensembl'] = dbxrefs['ensembl']
        if 'entrez' in dbxrefs:
            dbx['Entrez'] = dbxrefs['entrez']
        setattr(self, 'dbxref', dbx)

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        okeys = ['symbol', 'biotype', 'description']
        for key in keys:
            if key not in okeys:
                okeys.append(key)
        return okeys

    def get_name(self):
        return getattr(self, "symbol")

    def get_sub_heading(self):
        return getattr(self, "description")

    def get_diseases(self):
        return ['atd', 'cro', 'jia', 'ra', 'sle', 't1d', 'ibd', 'ssc', 'vit']

    def get_link_id(self):
        ''' Id used in generating page link. '''
        return getattr(self, "dbxrefs")['ensembl']

    def url(self):
        ''' Document page. '''
        return reverse('gene_page') + '?g='

    def comparable(self):
        ''' Document(s) can be compared. '''
        return True
