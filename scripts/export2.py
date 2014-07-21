import xml.etree.ElementTree as ET
import itertools
import unicodedata # Used ?
import re
import ast
import codecs
import argparse

from collections import defaultdict

DICTS_DIR = '/home/bartek/Projects/affiliation-parsing/dicts/'

AVAILABLE_FEATURES = [
        'Word',
        'Capital',
        'AllCapital',
        'Number',
        'Punct',
        'StopWord',
        'Country',
    ]

features_on = []
dicts = {}



def dict_from_file(filename):
    d = defaultdict(list)
    with codecs.open(DICTS_DIR + filename, 'rb', encoding='utf8') as f:
        for line in f:
            tokens = [t.lower().encode('utf8') for t in split_into_tokens(line)]
            for (nb, token) in enumerate(tokens):
                d[token] += [(tokens, nb)]
                print d[token]
        return d


def load_dicts(dd):
    what_where = [
            ('StopWord', 'stop_words2.txt'),
            ('Country', 'countries.txt'),
        ]

    for (what, where) in what_where:
        if what in features_on:
            dd[what] = dict_from_file(where)


def allcapital(word):
    return all(c.isupper() for c in word)


def firstcapital(word): # Mr and M but not MR, makes sense ???
    return word[0].isupper() and not any(c.isupper() for c in word[1:])


def get_local_features(token):

    assert len(token) >= 1

    features = []
    
    ntoken = token.lower().encode('utf8')

    if 'Word' in features_on:
        features += [ntoken]
    
    if token.isalpha():

        if 'Capital' in features_on:
            if firstcapital(token):
                features += ['Capital']

        if 'AllCapital' in features_on:
            if allcapital(token):
                features += ['AllCapital']

    elif token.isdigit():

        if 'Number' in features_on:
            features = ['Number']

    else:
        assert len(token) == 1, token

        if 'Punct' in features_on:
            features += ['Punct']

    return features


def matches((l1, p1), (l2, p2)):
    offset = p1 - p2
    print l1[offset:offset+len(l2)], l2
    return l1[offset:offset+len(l2)] == l2


def get_dict_features(token_list):
    token_list = [t.lower().encode('utf8') for t in token_list]
    features = []
    for (nb, token) in enumerate(token_list):
        cfeatures = []
        for (feature, d) in dicts.items():
            possible_hits = d[token]
            for phit in possible_hits:
                if matches((token_list, nb), phit):
                    cfeatures += [feature]
                    break
        features += [cfeatures]
    return features


def get_timesteps(token_list):
    local_features = [get_local_features(t) for t in token_list]
    dict_features = get_dict_features(token_list)

    features = [glue_lists(fts) for fts in zip(local_features, dict_features)] 

    return features


def glue_lists(lol):
    return list(itertools.chain(*lol))


def split_more(format_str, split_list, flags=0):
    pres = [re.split(format_str, string, flags=flags) for string in split_list]
    return glue_lists(pres)


def split_into_tokens(text):
    text = text or ''
    #text = convert_string(text) # Encoding issues?
    split_list = [text]
    split_list = split_more('\s+', split_list)
    split_list = split_more('(\W|_)', split_list, flags=re.U)
    split_list = split_more('(\d+)', split_list)
    return filter(lambda x: x != '', split_list)


def get_labels(text, label):
    return [(t, label) for t in split_into_tokens(text)]


def create_instance(aff, f):
    full_text = ''.join(t for t in aff.itertext())
    token_list = split_into_tokens(full_text)


    labeled_list = []
    labeled_list += get_labels(aff.text, 'NONE')
    for item in aff:
        labeled_list += get_labels(item.text, item.tag.upper()[:4])
        labeled_list += get_labels(item.tail, 'NONE')

    token_list2, label_list = zip(*labeled_list)

    assert token_list == list(token_list2), \
            '%r %r' % (token_list, token_list2) # If not, the training data may be faulty

    time_steps = get_timesteps(token_list)
    for (label, features) in zip(label_list, time_steps):
        print >> f, '%s ---- %s' % (label, ' '.join(features))


def create_input(li, f):
    #if 'Rare' in features_on:
    #    count_rare(li)
    for aff in li:
        create_instance(aff, f)
        print >> f


def export_to_crf_input(root, num, file1, file2):
    affs = list(root)
    aff_list = [(affs[0:num], file1), (affs[num:2*num], file2)]

    for (li, f) in aff_list:
        create_input(li, f)


def get_args():
    parser = argparse.ArgumentParser(description="Export tokens to crf format")
    
    parser.add_argument('features', default='[]')
    parser.add_argument('--number', type=int, dest='number', default=100)
    parser.add_argument('--train', dest='training_file', default='crf/data/fancy_train.txt')
    parser.add_argument('--test', dest='test_file', default='crf/data/fancy_test.txt')
    parser.add_argument('--input', dest='input_file', default='resources/final.xml')
    
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    features_on = ast.literal_eval(args.features)
    assert set(features_on) <= set(AVAILABLE_FEATURES)

    print features_on
    file1 = open(args.training_file, 'wb')
    file2 = open(args.test_file, 'wb')

    load_dicts(dicts)
    tree = ET.parse(args.input_file)
    root = tree.getroot()
    export_to_crf_input(root, args.number, file1, file2)
