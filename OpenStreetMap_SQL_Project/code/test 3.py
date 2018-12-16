# -*- coding: utf-8 -*-
"""
Created on Fri Mar 09 21:11:04 2018

@author: USUS
"""

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    elem_dict = {}
    for _, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag in elem_dict:
            elem_dict[elem.tag] += 1
        else:
            elem_dict[elem.tag] = 1
    return elem_dict
def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    
    

if __name__ == "__main__":
    test()
