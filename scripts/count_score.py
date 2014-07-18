import sys
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


def read_file(filename, one_number):
    with open(filename, 'rb') as f:
        t_lbng = []
        lbng = []

        correct = 0.0
        total = 0.0
        accuracy = 0.0
        at = 0.0
        ac = 0.0
        best = 0.0

        for line in f:
            tokens = line.split()
            if len(tokens) == 0: # Next affiliation
                (c, t) = check_labelings(t_lbng, lbng)
                correct += c
                total += t

                ac += t_lbng == lbng
                at += 1

                t_lbng = []
                lbng = []
            elif len(tokens) == 1: # Joint score, next test
                accuracy = float(tokens[0])
                score = correct / total
                best = max(score, best)

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


if __name__ == '__main__':
    input_file = 'crf/acrf_output_Testing.txt'

    args = sys.argv[1:]
    one_number = False

    if len(args) >= 1:
        input_file = args[0]
        if len(args) == 2:
            one_number = True

    read_file(input_file, one_number)
