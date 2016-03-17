from rest_framework import serializers, viewsets
from core.rest_framework.feature_resources import ListLocationsMixin


class LocationsSerializer(serializers.Serializer):
    feature = serializers.CharField(help_text='feature')
    chr = serializers.CharField(help_text='chromosome')
    start = serializers.IntegerField(help_text='start position')
    end = serializers.IntegerField(help_text='end position')


class LocationsViewSet(ListLocationsMixin, viewsets.ReadOnlyModelViewSet):
    ''' Returns feature (e.g. gene, marker, region) positions. '''
    serializer_class = LocationsSerializer
    filter_fields = ('feature', 'build')
