''' Generic feature document. '''
from elastic.result import Document
from elastic.elastic_settings import ElasticSettings


class PydginDocument(Document):

    @staticmethod
    def factory(hit):
        ''' Factory method for creating specific document object based on
        index type of the hit.
        @type  hit: dict
        @param hit: Elasticsearch hit.
        '''
        (idx, idx_type) = ElasticSettings.get_idx_key_by_name(hit['_index'], idx_type_name=hit['_type'])
        if idx is None or idx_type is None:
            return PydginDocument(hit)

        doc_class = ElasticSettings.get_label(idx, idx_type, label='class')
        return doc_class(hit) if doc_class is not None else PydginDocument(hit)

    def get_name(self):
        ''' Overridden get feature name. '''
        raise NotImplementedError("Inheriting class should implement this method")


class FeatureDocument(PydginDocument):
    ''' A feature (e.g. gene, marker) document. '''

    def get_position(self, build=None):
        ''' Overridden get feature name. '''
        raise NotImplementedError("Inheriting class should implement this method")
