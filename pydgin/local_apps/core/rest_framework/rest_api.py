''' Core DRF web-services. '''
from rest_framework import serializers, viewsets
from core.rest_framework.feature_resources import ListLocationsMixin


class LocationsSerializer(serializers.Serializer):
    ''' Serializer for locations. '''
    feature = serializers.CharField(help_text='feature')
    chr = serializers.CharField(help_text='chromosome')
    start = serializers.IntegerField(help_text='start position')
    end = serializers.IntegerField(help_text='end position')
    locusString = serializers.CharField(help_text='locus')


class LocationsViewSet(ListLocationsMixin, viewsets.ReadOnlyModelViewSet):
    ''' Given a feature (e.g. gene, marker, region) and the build return the location(s). '''
    serializer_class = LocationsSerializer
    filter_fields = ('feature', 'build')
