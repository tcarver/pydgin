from django import template

register = template.Library()


@register.inclusion_tag('gene/studies_section.html')
def show_studies_section(ens_id):
    ''' Template inclusion tag to render an studies section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/interactions_section.html')
def show_interactions_section(ens_id):
    ''' Template inclusion tag to render an interaction section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/genesets_section.html')
def show_genesets_section(ens_id):
    ''' Template inclusion tag to render an interaction section given a
    ensembl ID. '''
    return {'ens_id': ens_id}


@register.inclusion_tag('gene/phenotype_section.html')
def show_phenotype_section(dbxrefs):
    if 'mmusculus' in dbxrefs['orthologs']:
        return {'mgi': dbxrefs['orthologs']['mmusculus']['MGI']}
    return {}
