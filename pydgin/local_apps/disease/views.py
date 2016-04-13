''' Disease views. '''
from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView

from elastic.elastic_settings import ElasticSettings
from elastic.query import Query
from elastic.search import ElasticQuery, Search
from region.document import DiseaseLocusDocument
import gene


class DiseaseView(TemplateView):
    ''' Renders a disease page. '''
    template_name = "disease/index.html"

    def get_context_data(self, **kwargs):
        context = super(DiseaseView, self).get_context_data(**kwargs)
        disease = kwargs['disease'] if 'disease' in kwargs else self.request.GET.get('d')
        return DiseaseView.get_disease(self.request, disease, context)

    @classmethod
    def get_disease(cls, request, disease, context):
        disease = disease.lower()
        if disease is None:
            messages.error(request, 'No disease given.')
            raise Http404()
        query = ElasticQuery(Query.terms("code", [disease.split(',')]))
        elastic = Search(query, idx=ElasticSettings.idx('DISEASE', 'DISEASE'), size=5)
        res = elastic.search()
        if res.hits_total == 0:
            messages.error(request, 'Disease(s) '+disease+' not found.')
        elif res.hits_total < 9:
            disease_docs = res.docs
            names = ', '.join([getattr(doc, 'name') for doc in disease_docs])

            disease_docs = res.docs
            for dis in disease_docs:
                docs = DiseaseLocusDocument.get_disease_loci_docs(getattr(dis, 'code'))
                visible_hits = DiseaseLocusDocument.get_hits([h for r in docs for h in getattr(r, 'hits')])
                regions = []
                ens_all_cand_genes = []
                for r in docs:
                    region = r.get_disease_region(visible_hits)
                    if region is not None:
                        regions.append(region)
                        ens_all_cand_genes.extend(region['ens_cand_genes'])

                # get ensembl to gene symbol mapping for all candidate genes
                all_cand_genes = gene.utils.get_gene_docs_by_ensembl_id(ens_all_cand_genes)
                for region in regions:
                    region['cand_genes'] = {cg: all_cand_genes[cg] for cg in region.pop("ens_cand_genes", None)}
                setattr(dis, 'regions', regions)

            context['features'] = disease_docs
            context['title'] = names

            return context
        raise Http404()
