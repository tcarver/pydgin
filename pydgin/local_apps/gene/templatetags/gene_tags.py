from django import template

register = template.Library()


@register.inclusion_tag('gene/pub_section.html')
def show_pub_section(pmids):
    ''' Template inclusion tag to render a gene section given a
    chado gene feature. '''

    return {'pmids': pmids}

