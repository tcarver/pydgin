from django import template

register = template.Library()


@register.inclusion_tag('gene/pub_section.html')
def show_pub_section(pmids):
    ''' Template inclusion tag to render a publication section given a
    list of PMIDs. '''
    return {'pmids': pmids}


@register.inclusion_tag('gene/interactions_section.html')
def show_interactions_section(ens_id):
    ''' Template inclusion tag to render an interaction section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/phenotype_section.html')
def show_phenotype_section(dbxrefs):
    return {'mm_ens_id': dbxrefs['orthologs']['mmusculus']}
