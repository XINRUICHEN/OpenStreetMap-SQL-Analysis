# -*- coding: utf-8 -*-
"""
Created on Fri Mar 09 21:12:52 2018

@author: USUS
"""

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
    # You can use another testfile 'map.osm' to look at your solution
    # Note that the assertion below will be incorrect then.
    # Note as well that the test function here is only used in the Test Run;
    # when you submit, your code will be checked against a different dataset.
    keys = process_map('example.osm')
    pprint.pprint(keys)
    assert keys == {'lower': 6, 'lower_colon': 0, 'other': 1, 'problemchars': 1}


if __name__ == "__main__":
    test()