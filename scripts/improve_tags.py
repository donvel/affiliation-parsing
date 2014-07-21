import xml.etree.ElementTree as ET
import sys


keep_tags = ['addr-line', 'institution', 'country']

end_words = [',', ';', '.', ' and', ':', '`', '\'', '-', ', and', '\',', '; and']


def print_out(node):
    string = ET.tostring(node, encoding="utf-8")
    print string


def short_rep(order):
    return ''.join(s[0].upper() for s in order)


def process(root):
    for aff in root:
        order = []
        last = None
        for item in aff:
            item.tail = item.tail or ''
            item.text = item.text or ''

            if item.tail.strip() in [w.strip() for w in end_words]:
                item.text += ' ' + item.tail
                item.tail = ''
            elif item.tail.strip().startswith(','):
                item.text = item.text + ','
                item.tail = item.tail.strip()[1:]
            elif not any(item.text.strip().endswith(w) for w in end_words):
                item.text = item.text + ','
                if item.tail.strip():
                    print item.tail

            item.text += ' '
            item.tail += ' '

            tag = item.tag
            if tag in keep_tags and tag != last:
                last = tag
                order += [tag]
        rep = short_rep(order)

        if rep.startswith('AI'):
            for item in aff:
                tag = item.tag
                if tag == 'institution':
                    break
                if tag == 'addr-line':
                    item.tag = 'institution'

        if rep == 'IAC':
            aff.text = None

if __name__ == '__main__':

    input_file = 'resources/affiliations_stripped.xml'
    output_file = 'resources/final.xml'
    
    args = sys.argv[1:]
    print str(args)
    if len(args) >= 2:
        input_file = args[0]
        output_file = args[1]

    tree = ET.parse(input_file)
    root = tree.getroot()
    process(root)
    tree.write(output_file)
