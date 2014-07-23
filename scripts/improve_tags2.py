import xml.etree.ElementTree as ET
import argparse
import itertools
import codecs
import re


INSTITUTION_DICT = 'dicts/institution_keywords2.txt'


def set_from_file(filename):
    with codecs.open(filename, 'rb', encoding='utf8') as f:
        return set([l.rstrip() for l in f])


def norm(token):
    return token.lower() #.encode('utf8')


def glue_lists(lol):
    return list(itertools.chain(*lol))


def split_more(format_str, split_list, flags=0):
    pres = [re.split(format_str, string, flags=flags) for string in split_list]
    return glue_lists(pres)


def split_into_tokens(text):
    text = text or ''
    split_list = [text]
    split_list = split_more('(\s+)', split_list) # NOTE this is different than in export2.py, it keeps the \s
    split_list = split_more('(\W|_)', split_list, flags=re.U)
    split_list = split_more('(\d+)', split_list)
    return filter(lambda x: x != '', split_list)


def get_tokens(item):
    return [norm(t) for t in split_into_tokens(item.text)]


def make_elem(tag, text):
    el = ET.Element(tag)
    el.text = text
    return el

def print_out(node):
    string = ET.tostring(node, encoding="utf-8")
    print string


def split_by_commas(root):
    for aff in root:
        new_items = []
        for item in aff:
            current_text = u''
            tokens = split_into_tokens(item.text)
            for t in tokens:
                current_text += t
                if t in [',', ';']:
                    new_items += [make_elem(item.tag, current_text)]
                    current_text = u''
            if current_text:
                #if current_text.strip():
                #    print current_text
                new_items += [make_elem(item.tag, current_text)]
            new_items[len(new_items) - 1].tail = item.tail

        for item in list(aff):
            aff.remove(item)
        
        aff.extend(new_items)



def process(root):

    split_by_commas(root)

    institution_keywords = set_from_file(INSTITUTION_DICT)

    for aff in root:
        for item in aff:
            if item.tag == 'addr-line':
                tokens = get_tokens(item)
                if any(t in institution_keywords for t in tokens) and not any(t.isdigit() for t in tokens):
                    item.tag = 'institution'
                    print_out(item)


def get_args():
    parser = argparse.ArgumentParser(description="Dict-based training data enhancment")
    
    parser.add_argument('--input', default='resources/improved.xml')
    parser.add_argument('--output', default='resources/improved2.xml')
    
    return parser.parse_args()

if __name__ == '__main__':

    args = get_args()

    tree = ET.parse(args.input)
    root = tree.getroot()
    process(root)
    tree.write(args.output)
