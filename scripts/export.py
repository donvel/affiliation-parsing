import xml.etree.ElementTree as ET
import sys
import re
import itertools
import unicodedata
import random
import ast

n_dist = 0

n_features = None

features_on = [
        'Word',
        'Capital',
        'AllCapital',
        'Number',
        'Punct',
        #'StopWord', # This one is poor
    ]

stop_words = None


DICTS_DIR = '/home/bartek/Projects/affiliation-parsing/dicts/'


def set_from_file(filename):
    with open(DICTS_DIR + filename, 'rb') as f:
        return set([line.rstrip() for line in f])


def load_dicts():
    if 'StopWord' in features_on:
        global stop_words
        stop_words = set_from_file('stop_words2.txt') # stop_words.txt is too long


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
    
    if 'StopWord' in features_on:
        if lword in stop_words:
            res += ['StopWord']

    if lword.isalpha():
        if firstcapital(word) and 'Capital' in features_on:
            res += ['Capital']
        elif allcapital(word) and 'AllCapital' in features_on:
            res += ['AllCapital']

    elif lword.isdigit():
        if 'Number' in features_on:
            res = ['Number']

    else:
        assert len(lword) == 1, lword
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
    split_list = split_more('(\W|_)', split_list)
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
        write_tokens(item.tail, 'NONE', f)


def all_words(aff):
    return []


def count_rare(li):
    words = glue_lists([all_words(aff) for aff in li])


def write_affs(li, f):
    if 'Rare' in features_on:
        count_rare(li)
    for aff in li:
        write_aff(aff, f)
        print >> f

def export_to_crf_input(root, num, file1, file2):
    affs = list(root)
    # random.shuffle(affs)
    aff_list = [(affs[0:num], file1), (affs[num:2*num], file2)]

    for (li, f) in aff_list:
        write_affs(li, f)


if __name__ == '__main__':
    random.seed(1500)
    num = 50
    training_file = 'crf/data/fancy_train.txt'
    test_file = 'crf/data/fancy_test.txt'
    input_file = 'resources/affiliations_stripped.xml'

    args = sys.argv[1:]

    if len(args) >= 1:
        num = int(args[0])
        if len(args) >= 4:
            training_file = args[1]
            test_file = args[2]
            input_file = args[3]
            if len(args) >= 5:
                features_on = ast.literal_eval(args[4])

    print features_on
    file1 = open(training_file, 'wb')
    file2 = open(test_file, 'wb')

    load_dicts()
    tree = ET.parse(input_file)
    root = tree.getroot()
    export_to_crf_input(root, num, file1, file2)
