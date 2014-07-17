import xml.etree.ElementTree as ET
import sys
import re
import itertools
import unicodedata
import random


features_on = [
        'Word',
        'Capital',
        'AllCapital',
        'Number',
        'Punct',
    ]


def glue_lists(lol):
    return list(itertools.chain(*lol))


def allcapital(word):
    return all(c.isupper() for c in word)


def firstcapital(word):
    return word[0].isupper() and not any(c.isupper() for c in word[1:])


def get_tokens(word):
    res = []
    
    lword = word.lower()
    assert len(lword) >= 1
    
    if 'Word' in features_on:
        res += [lword]

    if lword.isalpha():
        if firstcapital(word) and 'Capital' in features_on:
            res += ['Capital']
        elif allcapital(word) and 'AllCapital' in features_on:
            res += ['AllCapital']

    elif lword.isdigit():
        if 'Number' in features_on:
            res = ['Number']

    else:
        assert len(lword) == 1
        if 'Punct' in features_on:
            res += ['Punct']

    return res


def convert_string(text):
    if isinstance(text, str):
        return text
    return unicodedata.normalize('NFKD', text).encode('ascii','ignore')


def split_more(format_str, split_list):
    pres = [re.split(format_str, string) for string in split_list]
    return glue_lists(pres)


def split_text(text):
    text = convert_string(text)
    split_list = re.split('\s+', text)
    split_list = split_more('(\W)', split_list)
    split_list = split_more('(\d+)', split_list)
    filtered_list = filter(lambda x: x != '', split_list)
    return [get_tokens(word) for word in filtered_list]


def write_tokens(text, label, f):
    if not text:
        return
    lines = split_text(text)
    for line in lines:
        print >> f, '%s ---- %s' % (label, ' '.join(line))


def write_aff(aff, f):
    write_tokens(aff.text, 'NONE', f)
    for item in aff:
        write_tokens(item.text, item.tag.upper()[:4], f)
        write_tokens(aff.text, 'NONE', f)


def export_to_crf_input(root, num, file1, file2):
    affs = list(root)
    random.shuffle(affs)
    aff_list = [(affs[0:num], file1), (affs[num:2*num], file2)]

    for (li, f) in aff_list:
        for aff in li:
            write_aff(aff, f)
            print >> f


if __name__ == '__main__':
    random.seed(1500)
    num = 50
    training_file = 'crf/data/fancy_train.txt'
    test_file = 'crf/data/fancy_test.txt'
    input_file = 'resources/affiliations_stripped.xml'

    args = sys.argv[1:]

    if len(args) >= 1:
        num = int(args[0])
        if len(args) == 4:
            training_file = args[1]
            test_file = args[2]
            input_file = args[3]

    file1 = open(training_file, 'wb')
    file2 = open(test_file, 'wb')

    tree = ET.parse(input_file)
    root = tree.getroot()
    export_to_crf_input(root, num, file1, file2)
