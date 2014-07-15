import csv
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from operator import itemgetter

keep_tags = ['addr-line', 'institution', 'country']
label_tags = ['label', 'bold', 'sup']
replace_tags = {'break': ' '}

def addstr(str1, str2):
    return (str1 or '') + (str2 or '')

def getstr(item):
    text = replace_tags.get(item.tag, None) or item.text
    return addstr(text, item.tail)

def is_label(item):
    return item.tag in label_tags and len(item.text) <= 2

def process(root):
    for aff in list(root):
        last_item = None

        for item in list(aff):

            # Expand children
            for item2 in list(item):
                my_text = getstr(item2)
                item.text = addstr(item.text, my_text)
                for item3 in list(item2):
                    raise Exception("To deep (lvl 3)")
                item.remove(item2)
            
            if item.tag not in keep_tags:
                my_text = None
                if (last_item is None and is_label(item)):
                    # We don't need the text content
                    my_text = item.tail
                else:
                    my_text = getstr(item)

                if last_item is not None:
                    last_item.tail = addstr(last_item.tail, my_text)
                else:
                    aff.text = addstr(aff.text, my_text)

                aff.remove(item)

            else: # Rozwijamy potomkow
                last_item = item
    pass

if __name__ == '__main__':
    input_file = '../resources/affiliations.xml'
    output_file = '../resources/affiliations_stripped.xml'

    args = sys.argv[1:]
    print str(args)
    if len(args) == 2:
        input_file = args[0]
        output_file = args[1]
    
    tree = ET.parse(input_file)
    root = tree.getroot()
    process(root)
    tree.write(output_file, encoding="utf-8")


