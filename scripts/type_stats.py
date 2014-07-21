import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import sys
from operator import itemgetter
from collections import defaultdict


keep_tags = ['addr-line', 'institution', 'country']
funny_types = ['IAIAC']

show_none = True



def print_out(node):
    string = ET.tostring(node, encoding="utf-8")
    print string


def get_list(ddict):
    return sorted(ddict.items(), key=itemgetter(1), reverse=True)


def short_rep(order):
    return ''.join(s[0].upper() for s in order)


def count_types(root):
    types = defaultdict(int)
    for aff in root:
        order = []
        last = None

        if aff.text and show_none:
            order += ['none']
            last = 'none'

        for item in aff:
            tag = item.tag
            if tag in keep_tags and tag != last:
                last = tag
                order += [tag]
            if item.tail and show_none:
                order += ['none']
                last = 'none'

        rep = short_rep(order)
        types[rep] += 1
        if rep in funny_types:
            print_out(aff)
    return get_list(types)

if __name__ == '__main__':

    input_file = 'resources/affiliations_stripped.xml'
    
    args = sys.argv[1:]
    print str(args)
    if len(args) >= 1:
        input_file = args[0]

    tree = ET.parse(input_file)
    root = tree.getroot()
    types = count_types(root)
    for (type, nbr) in types:
        print str(type) + " : " + str(nbr)

