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
    'MarkerView': OrderedDict([
        ('overview', True),
        ('historical ids', True),
        ('ld search', True)]),
    'StudyView': OrderedDict([
        ('overview', True)]),
    'DiseaseView': OrderedDict([
        ('overview', True)]),
    'RegionView': OrderedDict([
        ('overview', True)])
}