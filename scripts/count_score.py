import argparse
""" Returns a labeling score:
    Let T = sum_(s - an affiliation) (# of labels in the target labeling of s)
    C = sum_s (# of labels l in the target labeling of s such that
        the occurences of l in s are exactly the same in the tested labeling)
    The score equals C / T
"""

def check_labelings(target_lbng, lbng):
    processed = []
    total = 0
    correct = 0
    for label in target_lbng:
        if label not in processed:
            processed += [label]
            target_positions = [x == label for x in target_lbng]
            positions = [x == label for x in lbng]
            total += 1
            if positions == target_positions:
                correct += 1
    return (correct, total)


def get_tokens(hint_file):
    tokens = []
    ctokens = []
    with open(hint_file, 'rb') as hint:
        for line in hint:
            l = line.rstrip()
            if l:
                ctokens += [l]
            else:
                tokens += [ctokens]
                ctokens = []
    return tokens


def print_aff(aff, lb, f):
    extend = {'INST': 'institution', 'ADDR': 'addr-line', 'COUN': 'country'}
    last_label = 'NONE'

    print >>f, '<aff>'

    for (word, l) in zip(aff, lb):
        if l != last_label:
            if last_label != 'NONE':
                f.write('</%s>' % extend[last_label])
            if l != 'NONE':
                f.write('<%s>' % extend[l])

            last_label = l
        f.write(word + ' ')

    if last_label != 'NONE':
        f.write('</%s>' % extend[last_label])

    print >>f, '</aff>'


def show_errors(labeling, hint_file, error_file):
    tokens = get_tokens(hint_file)
    assert len(labeling) == len(tokens)
    with open(error_file, 'wb') as error:


        print >>error, "<affs>"

        for (aff, (lb_t, lb2)) in zip(tokens, labeling):
        
            assert len(aff) == len(lb_t)
            
            if lb_t != lb2:

                print_aff(aff, lb_t, error)
                print_aff(aff, lb2, error)

                print >>error, "<br>"

        print >>error, "</affs>"

def read_file(filename, hint_file, error_file, one_number):
    with open(filename, 'rb') as f:
        t_lbng = []
        lbng = []

        correct = 0.0
        total = 0.0
        accuracy = 0.0
        at = 0.0
        ac = 0.0
        best = 0.0

        best_labeling = []
        c_labeling = []

        for line in f:
            tokens = line.split()
            if len(tokens) == 0: # Next affiliation
                (c, t) = check_labelings(t_lbng, lbng)
                c_labeling += [(t_lbng, lbng)]
                correct += c
                total += t

                ac += t_lbng == lbng
                at += 1

                t_lbng = []
                lbng = []
            elif len(tokens) == 1: # Joint score, next test
                accuracy = float(tokens[0])
                score = correct / total
                if score > best:
                    best = score
                    best_labeling = c_labeling
                c_labeling = []

                if not one_number:
                    print 'S: %f, LA: %f, GA: %f' % \
                            (score, accuracy, ac / at)

                correct = 0.0
                total = 0.0
                ac = 0.0
                at = 0.0
            else: # (target, given)
                assert len(tokens) == 2
                t_lbng += [tokens[0]]
                lbng += [tokens[1]]

        print best, score
        show_errors(best_labeling, hint_file, error_file)


def get_args():
    parser = argparse.ArgumentParser(description="Count score and generate error file")
    
    parser.add_argument('--input_file', dest='input_file', default='acrf_output_Testing.txt')
    parser.add_argument('--hint_file', dest='hint_file', default='crf/data/fancy_hint.txt')
    parser.add_argument('--error_file', dest='error_file', default='crf/data/fancy_err.txt')
    parser.add_argument('--one_number', type=bool, dest='one_number', default=True)
    
    return parser.parse_args()



if __name__ == '__main__':

    args = get_args()

    read_file(args.input_file, args.hint_file, args.error_file, args.one_number)
