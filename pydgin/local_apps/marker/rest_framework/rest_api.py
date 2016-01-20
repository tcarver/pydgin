''' API for the RServe REST resources. '''
from rest_framework import serializers, viewsets
from marker.rest_framework.rserve_resources import ListLDMixin


class LDSerializer(serializers.Serializer):
    ''' Rserve LD resource. '''

    class LD(serializers.Serializer):
        marker2 = serializers.CharField(help_text='marker 2')
        dprime = serializers.FloatField(help_text='D prime')
        rsquared = serializers.FloatField(help_text='R squared')
        MAF = serializers.FloatField(required=False, help_text='Minor allele frequency')
        position = serializers.IntegerField(required=False, help_text='Position of variant 2')

    ld = serializers.ListField(child=LD())
    error = serializers.CharField(required=False)


class LDViewSet(ListLDMixin, viewsets.ReadOnlyModelViewSet):
    """
    Returns markers in LD with a given variant.
    """
    serializer_class = LDSerializer
    lookup_url_kwarg = "m1"
    lookup_fields = ('m1')
    filter_fields = ('m1', 'dataset', 'm2', 'window_size', 'dprime',
                     'rsq', 'maf', 'build', 'pos')
