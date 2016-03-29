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
    ---
    list:
        parameters:
            - name: m1
              description: marker to identify markers in LD with.
              required: true
              type: string
            - name: m2
              description: optional marker to calculate LD for marker1, Defaults to NULL.
              required: false
              type: string
            - name: window_size
              description: window size to look for markers in LD, Defaults to 1000000.
              required: false
              type: integer
            - name: dprime
              description: dprime to use, Defaults to 0.
              required: false
              type: float
            - name: rsq
              description: R square threshold, Defaults to 0.8.
              required: false
              type: float
            - name: maf
              description: if TRUE report the MAF in the result.
              required: false
              type: string
            - name: position
              description: if TRUE report the position in the result.
              required: false
              type: boolean
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
