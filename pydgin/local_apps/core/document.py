''' Generic documents based on elasticsearch documents. '''
from elastic.result import Document
from elastic.elastic_settings import ElasticSettings


class PydginDocument(Document):
    ''' A general pydgin feature document (e.g. publication). '''

    @staticmethod
    def factory(hit):
        ''' Factory method for creating types of documents based on
        their elasticsearch index type.
        @type  hit: dict
        @param hit: elasticsearch hit.
        '''
        (idx, idx_type) = ElasticSettings.get_idx_key_by_name(hit['_index'], idx_type_name=hit['_type'])
        if idx is None or idx_type is None:
            return PydginDocument(hit)

        doc_class = ElasticSettings.get_label(idx, idx_type, label='class')
        return doc_class(hit) if doc_class is not None else PydginDocument(hit)

    def get_name(self):
        ''' Override get pydgin document name. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_sub_heading(self):
        ''' Overridden get feature sub-heading. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_diseases(self):
        ''' Overridden get diseases for feature. '''
        raise NotImplementedError("Inheriting class should implement this method")


class ResultCardMixin(object):
    ''' Result card object. '''
    EXCLUDED_RESULT_KEYS = []

    def url(self):
        ''' Document page url. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def get_link_id(self):
        ''' Page link id. '''
        return NotImplementedError("Inheriting class should implement this method")

    def is_external(self):
        ''' External document link. '''
        return False

    def comparable(self):
        ''' Document(s) can be compared. '''
        return False

    def result_card_process_attrs(self):
        ''' Override to carry out any processing of document attributes for displaying. '''
        pass

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        self.result_card_process_attrs()
        keys = set([k for k in self.__dict__.keys() if k not in self.EXCLUDED_RESULT_KEYS and k is not '_meta'])
        if self.highlight() is not None:
            keys |= set(self.highlight().keys())
        return sorted(list(keys))


class FeatureDocument(PydginDocument, ResultCardMixin):
    ''' A feature (e.g. gene, marker) document. '''

    def get_position(self, build=38):
        '''
        Overridden get feature position by build.
        @type  build: integer
        @keyword build: NCBI build to return position for.
         '''
        raise NotImplementedError("Inheriting class should implement this method")


class PublicationDocument(PydginDocument, ResultCardMixin):
    ''' Publication document. '''
    EXCLUDED_RESULT_KEYS = ['pmid']

    def get_name(self):
        ''' Document name. '''
        return getattr(self, 'pmid')

    def get_link_id(self):
        ''' Page link id. '''
        return self.get_name()

    def url(self):
        ''' Document page url. '''
        return "http://www.ncbi.nlm.nih.gov/pubmed/"

    def is_external(self):
        ''' External document link. '''
        return True

    def result_card_keys(self):
        ''' Gets the keys of the document object as an ordered list to show in the result card. '''
        keys = super().result_card_keys()
        okeys = ['title']
        for key in keys:
            if key not in okeys:
                okeys.append(key)
        return okeys
