# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 13:26:03 2018

@author: USUS
"""

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import sys
sys.path.append("C:/Users/USUS/Desktop/Uda-DS/code/schema.py")
import schema
OSM_PATH = "C:/Users/USUS/desktop/Uda-DS/pro1/chicago_illinois_sample2.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
SCHEMA = schema.schema
# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
def no_sub_tag(element):
    if len(element.getchildren()) == 0:
        return True
    else:
        return False
def fix_node_tag(element):
# print(element.attrib['id'])
    node_tags = []
    node_tags_iter = element.iter('tag')
    for i in node_tags_iter:
        node_tags_dict = {}
    # print(i.attrib['k'])
        k_data = i.attrib['k']
        value_data = i.attrib['v']
        if PROBLEMCHARS.search(k_data):
            print("PROBLEMCHARS")
            pass
        elif LOWER_COLON.match(k_data):
        # print(k_data.split(':',maxsplit=1))
        # node_tags_dict['key'] = k_data.split(':',maxsplit=1)[1]
        # node_tags_dict['type'] = k_data.split(':', maxsplit=1)[0]
            node_tags_dict['key'] = k_data.split(':',1)[1]
            node_tags_dict['type'] = k_data.split(':',1)[0]
            node_tags_dict['value'] = value_data
            node_tags_dict['id'] = element.attrib['id']
            node_tags.append(node_tags_dict)
        else:
            node_tags_dict['key'] = k_data
            node_tags_dict['type'] = 'regular'
            node_tags_dict['value'] = value_data
            node_tags_dict['id'] = element.attrib['id']
            node_tags.append(node_tags_dict)
# print(node_tags)
    return node_tags

def fix_way_nodes(element):
    way_nodes = []
    way_nodes_iter = element.iter('nd')
    n = -1
    for i in way_nodes_iter:
        way_node_dict = {}
        n+=1
        way_node_dict["id"] = element.attrib['id']
        way_node_dict['node_id'] = i.attrib['ref']
        way_node_dict['position'] = n
        way_nodes.append(way_node_dict)
# print(way_nodes)
    return way_nodes

mapping = { "St.": "Street","Rd": "Road", "rd": "Road","RD":"Road",
           "Trl":"Trail","Rd.":"Road", "Ave": "Avenue",
           "Blvd": "Boulevard","Ct":"Court", "Ln":"Lane"}

def update_name(name, mapping):
    shortname = mapping.keys()
    for word in shortname:
        if word in name:
            name = name.replace(word,mapping[word])
    return name

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        if no_sub_tag(element):
            for k in node_attr_fields:
                node_attribs[k] = element.attrib[k]
        elif not no_sub_tag(element):
            for k in node_attr_fields:
                node_attribs[k] = element.attrib[k]
            tags = update_name(fix_node_tag(element),mapping)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        if no_sub_tag(element):
            for k in way_attr_fields:
                way_attribs[k] = element.attrib[k]
        elif not no_sub_tag(element):
            for k in way_attr_fields:
                way_attribs[k] = element.attrib[k]
            tags = update_name(fix_node_tag(element),mapping)
            way_nodes = fix_way_nodes(element)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'wb') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)