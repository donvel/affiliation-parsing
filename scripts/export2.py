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
        'Rare',

        # dict - based
        'StopWord',
        'Country',
    ]

features_on = []
dicts = {}
rare_thr = 2
nei_thr = 2


def norm(token):
    return token.lower().encode('utf8')


def dict_from_file(filename):
    d = defaultdict(list)
    with codecs.open(DICTS_DIR + filename, 'rb', encoding='utf8') as f:
        for line in f:
            tokens = [norm(t) for t in split_into_tokens(line)]
            for (nb, token) in enumerate(tokens):
                d[token] += [(tokens, nb)]
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


def get_local_features(token, rare_words=None):

    assert len(token) >= 1

    features = []
    
    ntoken = norm(token)

    if token.isalpha():

        if 'Capital' in features_on:
            if firstcapital(token):
                features += ['Capital']

        if 'AllCapital' in features_on:
            if allcapital(token):
                features += ['AllCapital']

        if 'Rare' in features_on:
            if ntoken in rare_words:
                features += ['Rare']

    elif token.isdigit():

        if 'Number' in features_on:
            features = ['Number']

    else:
        assert len(token) == 1, token

        if 'Punct' in features_on:
            features += ['Punct']
    
    if 'Word' in features_on:
        if not any(x in features for x in ['Rare', 'Number']):
            features += [ntoken]

    return features


def matches((l1, p1), (l2, p2)):
    offset = p1 - p2
    return l1[offset:offset+len(l2)] == l2


def get_dict_features(token_list):
    token_list = [norm(t) for t in token_list]
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


def find_rare_words(li):
    all_tokens = [norm(t)
             for aff in li
             for t in split_into_tokens(''.join(txt for txt in aff.itertext()))]
    freq = defaultdict(int)
    for token in all_tokens:
        freq[token] += 1
    rare = set(t for (t, f) in freq.items() if f <= rare_thr)
    return rare


def get_nei_features(features):
    nei_features = []
    for i in range(len(features)):
        cfeatures = []

        for j in range(-nei_thr, nei_thr + 1):
            if j == 0:
                continue
            k = i + j
            nfeatures = []
            if k < 0:
                nfeatures = ['Start']
            elif k >= len(features):
                nfeatures = ['End']
            else:
                nfeatures = features[k]
            cfeatures += [f + '@' + str(j) for f in nfeatures]

        nei_features += [cfeatures]

    return nei_features


def get_timesteps(token_list, rare_words=None):
    local_features = [get_local_features(t, rare_words=rare_words) for t in token_list]
    dict_features = get_dict_features(token_list)

    features = [glue_lists(fts) for fts in zip(local_features, dict_features)]

    nei_features = get_nei_features(features)
    features = [glue_lists(fts) for fts in zip(features, nei_features)]

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


def create_instance(aff, f, rare_words=None):
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

    time_steps = get_timesteps(token_list, rare_words=rare_words)
    for (label, features) in zip(label_list, time_steps):
        print >> f, '%s ---- %s' % (label, ' '.join(features))


def create_input(li, f):
    rare_words = set([])
    if 'Rare' in features_on:
        rare_words=find_rare_words(li)
    for aff in li:
        create_instance(aff, f, rare_words=rare_words)
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
    parser.add_argument('--rare', type=int, dest='rare', default=3)
    parser.add_argument('--neighbor', type=int, dest='neighbor', default=0)
    
    return parser.parse_args()


if __name__ == '__main__':

    args = get_args()

    features_on = ast.literal_eval(args.features)
    assert set(features_on) <= set(AVAILABLE_FEATURES)
    rare_thr = args.rare
    nei_thr = args.neighbor

    print features_on
    file1 = open(args.training_file, 'wb')
    file2 = open(args.test_file, 'wb')

    load_dicts(dicts)
    tree = ET.parse(args.input_file)
    root = tree.getroot()
    export_to_crf_input(root, args.number, file1, file2)
