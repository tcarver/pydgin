''' Django REST framework Elastic resources. '''
from rest_framework import serializers, viewsets
from elastic.rest_framework.resources import ListElasticMixin, ElasticLimitOffsetPagination,\
    RetrieveElasticMixin
from elastic.elastic_settings import ElasticSettings
from marker.rest_framework.rserve_resources import RetrieveLDMixin, ListLDMixin


class PublicationSerializer(serializers.Serializer):
    ''' Publication resource. '''

    class PublicationAuthor(serializers.Serializer):
        name = serializers.ReadOnlyField()
        initials = serializers.ReadOnlyField()

    pmid = serializers.IntegerField()
    title = serializers.ReadOnlyField()
    abstract = serializers.ReadOnlyField()
    journal = serializers.ReadOnlyField()
    authors = serializers.ListField(child=PublicationAuthor())
    date = serializers.DateField()
    tags = serializers.DictField()


class PublicationViewSet(RetrieveElasticMixin, ListElasticMixin, viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of publications.
    """
    serializer_class = PublicationSerializer
    pagination_class = ElasticLimitOffsetPagination
    idx = ElasticSettings.idx('PUBLICATION')
    filter_fields = ('pmid', 'title', 'authors__name', 'tags__disease')


class LDSerializer(serializers.Serializer):
    ''' Rserve LD resource. '''

    class LD(serializers.Serializer):
        marker2 = serializers.CharField(help_text='marker 2')
        dprime = serializers.FloatField(help_text='D prime')
        rsquared = serializers.FloatField(help_text='R squared')
        MAF = serializers.FloatField(required=False)
        position = serializers.IntegerField(required=False)
    ld = serializers.ListField(child=LD())


class LDViewSet(RetrieveLDMixin, ListLDMixin, viewsets.ReadOnlyModelViewSet):
    """
    Returns markers in LD with a given variant.
    """
    serializer_class = LDSerializer
    lookup_url_kwarg = "m1"
    lookup_fields = ('m1')
    filter_fields = ('m1', 'dataset', 'm2', 'window_size', 'dprime',
                     'rsq', 'maf', 'build', 'pos')
