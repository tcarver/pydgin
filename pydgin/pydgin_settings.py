''' Pydgin project settings. '''
from collections import OrderedDict
DEFAULT_BUILD = 38

''' Sections for pages. '''
PAGE_SECTIONS = {
    'GeneView': OrderedDict([
        ('overview', True),
        ('external links', True),
        ('study', True),
        ('publication', {'show': True}),
        ('interactions', True),
        ('genesets', True),
        ('phenotype links', True)]),
    'Marker': OrderedDict([
        ('overview', True)])
}
