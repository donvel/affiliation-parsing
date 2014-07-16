import xml.etree.ElementTree as ET
import sys
import re
import itertools
import unicodedata


def convert_string(text):
    if isinstance(text, str):
        return text
    return unicodedata.normalize('NFKD', text).encode('ascii','ignore')


def split_text(text):
    #return re.split('\s+', text)
    text = convert_string(text)
    split_list = [re.split('(\W+)', string) for string in re.split('\s+', text)]
    full_list = list(itertools.chain(*split_list))
    filtered_list = filter(lambda x: x != '', full_list)
    return filtered_list


def write_tokens(text, label):
    if not text:
        return
    words = split_text(text)
    for word in words:
        print '%s --- %s' % (label, word)


def write_aff(aff):
    write_tokens(aff.text, 'NONE')
    for item in aff:
        write_tokens(item.text, item.tag.upper())
        write_tokens(aff.text, 'NONE')


def export_to_crf_input(root, num_l, num_r):
    cnum = 0
    for aff in root:
        if cnum >= num_l and cnum <= num_r:
            write_aff(aff)
            print
        cnum += 1


if __name__ == '__main__':
    input_file = '../resources/affiliations_stripped.xml'
    #training_file = '../resources/crf_train.txt'
    #test_file = '../resources/crf_test.txt'
    num_l = 0
    num_r = 19

    args = sys.argv[1:]

    if len(args) >= 2:
        num_l = int(args[0])
        num_r = int(args[1])
    if len(args) == 3:
        input_file = args[2]

    tree = ET.parse(input_file)
    root = tree.getroot()
    export_to_crf_input(root, num_l, num_r)
