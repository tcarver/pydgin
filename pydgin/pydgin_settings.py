''' Pydgin project settings. '''
from collections import OrderedDict
DEFAULT_BUILD = 38

PAGE_SECTIONS = {
    'GeneView': OrderedDict([
        ('overview', True),
        ('external links', True),
        ('study', True),
        ('publication', True),
        ('interactions', True),
        ('genesets', True),
        ('phenotype links', True)]),
    'Marker': OrderedDict([
        ('overview', True)])
}
