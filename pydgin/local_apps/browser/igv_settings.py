''' Pydgin IGV Genome Browser settings '''
DEAFULT_GENOME = 'hg38'

''' Genomes available '''
GENOME_DETAILS = {
    'hg38': {
        'display_name': 'Human (GRCh38)',
        'locus': 'chr1:113,813,811-113,871,759',
        'tracks': {
            'genes': {'url': "/static/data/gencode.v21.collapsed.bed"}
        }
    },
    'hg19': {
        'display_name': 'Human (GRCh37)',
        'locus': 'chr1:114,356,432-114,414,375',
        'tracks': {
            'genes': {'url': "//igv.broadinstitute.org/annotations/hg19/genes/gencode.v18.collapsed.bed"}
        }
    },
#    'hg18': {
#        'display_name': 'Human (NCBI36)',
#        'locus': 'chr1:114,157,955-114,215,898',
#        'tracks': {
#            'genes': {'url': "//igv.broadinstitute.org/annotations/hg18/genes/gencode.v14.collapsed.bed"}
#        }
#    }
}

TRACK_DETAILS = {
    'genes': {
        'name': "Genes",
        'displayMode': "EXPANDED",
        'order': 1
    },
    'ic_cro_liu': {
        'url': "/static/data/rs2476601.gwas",
        'name': "CRO - Liu",
        'featureType': "gwas",
        'format': 'gwasSNPS',
        'order': 2,
        'variantURL': "/marker/",
    }
}
