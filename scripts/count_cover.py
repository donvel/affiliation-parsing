import xml.etree.ElementTree as ET
import sys
import matplotlib.pyplot as plt

def count_coverage(aff):
    tagged_text = 0
    free_text = len(aff.text or '')
    for item in aff:
        tagged_text += len(item.text or '')
        free_text += len(item.tail or '')
    total = tagged_text + free_text
    if total == 0:
        return 0
    else:
        # print tagged_text, total
        return tagged_text / float(total)

def print_out(node):
    string = ET.tostring(node, encoding="utf-8")
    print string

if __name__ == '__main__':
    input_file = '../resources/affiliations_stripped.xml'
    output_file = '../resources/affiliations_stripped_filtered.xml'
    threshold = 0.75

    args = sys.argv[1:]
    print str(args)
    if len(args) == 3:
        input_file = args[0]
        output_file = args[1]
        threshold = float(args[2])

    tree = ET.parse(input_file)
    root = tree.getroot()

    parts = []

    for aff in list(root):
        coverage = count_coverage(aff)
        parts += [coverage]
        if coverage < threshold:
            print_out(aff)
            root.remove(aff)

    tree.write(output_file, encoding="utf-8")

    n, bins, patches = plt.hist(parts, 50, normed=1, facecolor='g', alpha=0.75)

    plt.grid(True)
    plt.show()

