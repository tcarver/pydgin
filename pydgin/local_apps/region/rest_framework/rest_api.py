''' Region DRF web-services. '''
from rest_framework import serializers, mixins, renderers
from region.rest_framework.region_resources import ListRegionsMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
import csv
from six import StringIO


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


class GFFRenderer(renderers.BaseRenderer):
    ''' Render GFF format. '''
    media_type = 'text/gff'
    format = 'gff'

    def render(self, data, media_type=None, renderer_context=None):
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter="\t")
        header = self.header(renderer_context['request'])
        for hdr in header:
            csv_writer.writerow([hdr])

        for row in data:
            csv_writer.writerow(self.row_data(row))
        return csv_buffer.getvalue()

    def row_data(self, row):
        ''' GFF row data. '''
        raise NotImplementedError("Inheriting class should implement this method")

    def header(self, request):
        ''' List of GFF header lines. '''
        return ['##gff-version 3']


class DiseaseRegionGFFRenderer(GFFRenderer):
    ''' Render regions as in GFF format. '''
    def row_data(self, row):
        return [row['seqid'], 'immunobase', 'region', row['rstart'], row['rstop'],
                '.', '.', '.',
                'Name='+row['region_name']+';genes='+','.join(row['ens_cand_genes']) +
                ';markers='+','.join(row['markers']) +
                ';diseases='+','.join(row['all_diseases'])]

    def header(self, request):
        disease = request.GET.get('disease', 'T1D')
        return ['##gff-version 3', '##'+disease+' Regions from immunobase.org']


class DiseaseRegionViewSet(ListRegionsMixin, mixins.ListModelMixin, GenericViewSet):
    ''' Get the regions associated with a given disease (e.g. T1D, MS).
    ---
    list:
        response_serializer: DiseaseRegionSerializer
        parameters:
            - name: disease
              description: disease
              required: false
              type: string
              paramType: query
            - name: build
              description: genome build (e.g. hg38).
              required: false
              type: string
              paramType: query
        produces:
            - application/json
            - text/gff
    '''
    renderer_classes = (JSONRenderer, DiseaseRegionGFFRenderer, BrowsableAPIRenderer, )
    serializer_class = DiseaseRegionSerializer
    filter_fields = ('disease', 'build')
