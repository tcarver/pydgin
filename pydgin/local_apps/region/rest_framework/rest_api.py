''' Region DRF web-services. '''
from rest_framework import serializers, mixins
from region.rest_framework.region_resources import ListRegionsMixin
from rest_framework.viewsets import GenericViewSet


class GeneCategory(serializers.Serializer):
    ''' Genes found in and up/downstream of the region. '''
    region = serializers.DictField(required=False)
    downstream = serializers.DictField(required=False)
    upstream = serializers.DictField(required=False)


class DiseaseRegionSerializer(serializers.Serializer):
    ''' Serializer for locations. '''
    region_name = serializers.CharField(help_text='region_name')
    seqid = serializers.CharField(help_text='chromosome')
    rstart = serializers.IntegerField(help_text='start position')
    rstop = serializers.IntegerField(help_text='end position')
    all_diseases = serializers.ListField(help_text='all diseases')
    markers = serializers.ListField(help_text='markers')
    ens_cand_genes = serializers.ListField(help_text='candidate genes')
    genes = GeneCategory()


class DiseaseRegionViewSet(ListRegionsMixin, mixins.ListModelMixin, GenericViewSet):
    ''' Given a feature (e.g. gene, marker, region) and the build return the location(s).
    ---
    list:
        response_serializer: DiseaseRegionSerializer
        parameters:
            - name: feature
              description: gene, marker or region (e.g. IL2, rs2476601).
              required: false
              type: string
              paramType: query
            - name: build
              description: genome build (e.g. hg38).
              required: false
              type: string
              paramType: query
    '''
    serializer_class = DiseaseRegionSerializer
    filter_fields = ('disease', 'build')
