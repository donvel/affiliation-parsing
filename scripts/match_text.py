import xml.etree.ElementTree as ET
import itertools
import unicodedata # Used ?
import re
import ast
import codecs
import argparse
import unicodedata

from collections import defaultdict

NUM_LEN = len('2740170 ')


def full_text(node):
    return ''.join(t for t in node.itertext()).rstrip()


def get_dict(root, text_file):
    str_d = defaultdict(list)
    for line in text_file:
        num = int(line.split()[0])
        aff = line[NUM_LEN:].rstrip()
        str_d[num] += [aff]

    node_d = defaultdict(list)
    for aff in root:
        num = int(aff.get('num'))
        node_d[num] += [full_text(aff)]

    return str_d, node_d

def convert_string(text):
    if isinstance(text, str):
        return text
    return unicodedata.normalize('NFKD', text).encode('ascii','ignore')

# Tests if s1 is a subsequence of s2
def is_subseq(s1, s2):
    s1 = convert_string(s1)
    s2 = convert_string(s2)
    i = 0
    for l in s1:
        while s2[i] != l:
            i += 1
            if i == len(s2):
                return False
    return True


def get_matching(l1, l2):
    """
    for x in l1:
        if not any(is_subseq(x, y) for y in l2):
            print x
    """
    return len(filter(lambda x: any(is_subseq(x, y) for y in l2), l1))
    """
    mat = [[is_subseq(s1, s2) for s2 in l2] for s1 in l1]
    print mat
    success = all(len(filter(lambda x: x, v)) == 1 for v in mat)
    if not success:
        return [], False
    matching = [(s1, filter(lambda x: is_subseq(s1, x), l2)[0]) for s1 in l1]
    return matching, True
    """


def match_text(root, text_file, doc_num):
    str_dict, node_dict = get_dict(root, text_file)
    
    total = 0
    good = 0

    if doc_num != 0:
       str_list = str_dict[doc_num]
       node_list = node_dict[doc_num]

       matching, success = get_matching(node_list, str_list)
       print matching, success
    else:
       for (number, l1) in node_dict.items():
           """
           matching, success = get_matching(l1, str_dict[number])
           if success:
               good += len(l1)
           """
           good += get_matching(l1, str_dict[number])
           #"""
           total += len(l1)
       print good / float(total), good, total 


def get_args():
    parser = argparse.ArgumentParser(description="Wanna gork text into text, huh?")
    
    parser.add_argument('--xml', dest='xml', default='resources/set/affs-stripped.xml')
    parser.add_argument('--raw', dest='raw', default='resources/set/affs-string.txt')
    parser.add_argument('--doc', dest='doc', type=int, default=0)
    
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    text_file = codecs.open(args.raw, 'rb', encoding='utf8')

    tree = ET.parse(args.xml)
    root = tree.getroot()
    
    match_text(root, text_file, args.doc)

