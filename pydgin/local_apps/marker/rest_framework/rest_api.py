''' API for the RServe REST resources. '''
from rest_framework import serializers, viewsets
from marker.rest_framework.rserve_resources import ListLDMixin, ListPopulationMixin


class LDSerializer(serializers.Serializer):
    ''' Rserve LD resource. '''

    class LD(serializers.Serializer):
        marker2 = serializers.CharField(help_text='marker 2')
        dprime = serializers.FloatField(help_text='D prime')
        rsquared = serializers.FloatField(help_text='R squared')
        MAF = serializers.FloatField(required=False, help_text='Minor allele frequency')
        major = serializers.CharField(required=False, help_text='major allele')
        minor = serializers.CharField(required=False, help_text='minor allele')
        position = serializers.IntegerField(required=False, help_text='Position of variant 2')

    ld = serializers.ListField(child=LD(), help_text='list of marker(s) in ld')


class LDViewSet(ListLDMixin, viewsets.ReadOnlyModelViewSet):
    """
    Returns markers in LD with a given variant.
    """
    serializer_class = LDSerializer
    lookup_url_kwarg = "m1"
    lookup_fields = ('m1')
    filter_fields = ('m1', 'dataset', 'm2', 'window_size', 'dprime',
                     'rsq', 'maf', 'build', 'pos')


class PopulationsSerializer(serializers.Serializer):
    ''' Rserve population resource. '''

    class Population(serializers.Serializer):
        population = serializers.CharField(required=False, help_text='population')
        MAF = serializers.FloatField(required=False, help_text='Minor allele frequency')
        major = serializers.CharField(required=False, help_text='major allele')
        minor = serializers.CharField(required=False, help_text='minor allele')

    populations = serializers.ListField(child=Population(), help_text='population details (major/minor allele, MAF)')
    marker = serializers.CharField(help_text='marker')


class PopulationsViewSet(ListPopulationMixin, viewsets.ReadOnlyModelViewSet):
    """ Returns population stats for a given variant. """
    serializer_class = PopulationsSerializer
    filter_fields = ('marker')
