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
        ''' Overridden get pydgin document name. '''
        raise NotImplementedError("Inheriting class should implement this method")


class ResultCardMixin(object):
    ''' Result card object. '''

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


class FeatureDocument(PydginDocument, ResultCardMixin):
    ''' A feature (e.g. gene, marker) document. '''

    def get_position(self, build=None):
        '''
        Overridden get feature position by build.
        @type  build: integer
        @keyword build: NCBI build to return position for.
         '''
        raise NotImplementedError("Inheriting class should implement this method")


class PublicationDocument(PydginDocument, ResultCardMixin):
    ''' Publication document. '''

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
