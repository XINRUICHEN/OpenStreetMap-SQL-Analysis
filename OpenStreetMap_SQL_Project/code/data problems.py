# -*- coding: utf-8 -*-
"""
Created on Fri Mar 09 21:22:44 2018

@author: USUS
"""

import xml.etree.ElementTree as ET
import pprint
import re
from collections import defaultdict

# create small sample
OSM_FILE = ('C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois.osm')  # Replace this with your osm file
SAMPLE_FILE = ('C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois_sample2.osm')
k = 20 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _,root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))
    output.write('</osm>')
    
def count_tags(filename):
    elem_dict = {}
    for _, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag in elem_dict:
            elem_dict[elem.tag] += 1
        else:
            elem_dict[elem.tag] = 1
    return elem_dict
def test():
    tags = count_tags('C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois_sample2.osm')
    pprint.pprint(tags)
if __name__ == "__main__":
    test()
    
#这四大标记类别在字典中的各自数量：
#“lower”，表示仅包含小写字母且有效的标记，
#“lower_colon”，表示名称中有冒号的其他有效标记，
#“problemchars”，表示字符存在问题的标记，以及
#“other”，表示不属于上述三大类别的其他标记。
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
def key_type(element, keys):
    if element.tag == "tag":               
        flag = 0
        if re.search(lower, element.attrib["k"]):
            keys["lower"] += 1
            flag = 1
        if re.search(lower_colon, element.attrib["k"]):
            keys["lower_colon"] += 1
            flag = 1
        if re.search(problemchars, element.attrib["k"]):
            keys["problemchars"] += 1
            flag = 1
        if flag == 0:
            keys["other"] += 1        
    return keys
def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys
def test():
    keys = process_map('C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois_sample2.osm')
    pprint.pprint(keys)
if __name__ == "__main__":
    test()
    
#explore data problems
OSMFILE = "C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois_sample2.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
def print_sorted_dict(d):
    keys=d.keys()
    keys=sorted(keys,key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k,v)
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    pprint.pprint(dict(street_types))
    return street_types

if __name__ == '__main__':
    audit(OSMFILE)

# clean data code based on above exploration
OSMFILE = "C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois_sample2.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]
mapping = { "St.": "Street","Rd": "Road", "rd": "Road","RD":"Road",
           "Trl":"Trail","Rd.":"Road", "Ave": "Avenue",
           "Blvd": "Boulevard","Ct":"Court", "Ln":"Lane"}

def update_name(name, mapping):
    shortname = mapping.keys()
    for word in shortname:
        if word in name:
            name = name.replace(word,mapping[word])
    return name

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types



def test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"


if __name__ == '__main__':
    test()