''' Pydgin project settings. '''
from collections import OrderedDict
DEFAULT_BUILD = 38

''' Sections for pages. '''
PAGE_SECTIONS = {
    'GeneView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
#        ('igvBrowser', {'show': True, 'collapse': False}),
        ('external links', True),
        ('study', True),
        ('publication', {'show': True}),
        ('interactions', True),
        ('genesets', True),
        ('phenotype links', True)]),
    'MarkerView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
#         ('igvBrowser', {'show': True, 'collapse': False}),
        ('historical ids', True),
        ('linkage disequilibrium statistics', True)]),
    'StudyView': OrderedDict([
        ('overview', True)]),
    'DiseaseView': OrderedDict([
        ('overview', True)]),
    'RegionView': OrderedDict([
        ('overview', {'show': True, 'collapse': False}),
        ('igvBrowser', {'show': True, 'collapse': False}),
        ('publication', {'show': True})]),
    'StudyView': OrderedDict([
        ('overview', True)])
}

CDN = {
    "JQUERY": "//code.jquery.com/jquery-2.2.0.min.js",
    "JQUERY_UI": "//code.jquery.com/ui/1.11.4/jquery-ui.js",
    "BOOTSTRAP": "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js",
    "QUNIT": "//code.jquery.com/qunit/qunit-1.21.0.js",
    "QUNIT_CSS": "//code.jquery.com/qunit/qunit-1.21.0.css",

    # CSS
    "JQUERY_UI_CSS": "//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css",
    "FONT_AWSUM": "//maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css",
}
