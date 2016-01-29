''' Marker documents.'''
from core.document import FeatureDocument
from django.core.urlresolvers import reverse


class MarkerDocument(FeatureDocument):
    ''' Marker document object.'''

    def get_name(self):
        return getattr(self, "id")

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        return reverse('marker_page') + '?m='


class ImmunoChipDocument(MarkerDocument):
    ''' ImmunoChip marker document. '''

    def get_name(self):
        return getattr(self, "name")
