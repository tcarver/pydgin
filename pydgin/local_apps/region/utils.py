'''
Created on 15 Jan 2016

@author: ellen

Utility functions for Regions.
'''

import logging

logger = logging.getLogger(__name__)


class Region(object):
    '''
    Region class to define functions for changing between regions/disease loci/hits in index.
    '''

    @classmethod
    def hit_to_region(cls, hit):
        print(hit)
