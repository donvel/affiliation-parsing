import sys
import re

head_template = \
    """<head>
    <style>
    institution {color: sienna;}
    addr-line {color: green;}
    country {color: salmon;}
    </style>
    <meta charset="utf-8">
    </head>"""


def process_files(input_file, output_file):
    with open(input_file, 'rb') as inp:
        with open(output_file, 'wb') as out:
            lines = list(inp)
            print >> out, '<html>'
        
            print >> out, head_template

            print >> out, "<body>"
            for line in lines:
                line = re.sub('affs', 'ol', line)
                line = re.sub('aff', 'li', line)
                print >> out, line
            print >> out, "</body>"

            print >> out, "</html>"

if __name__ == '__main__':
    input_file = 'resources/affiliations_stripped.xml'
    output_file = 'resources/affiliations_stripped.html'

    args = sys.argv[1:]
    print str(args)
    if len(args) >= 2:
        input_file = args[0]
        output_file = args[1]

    process_files(input_file, output_file)
