import argparse
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


def get_args():
    parser = argparse.ArgumentParser(description="Export xml to human-readable html")
    
    parser.add_argument('--xml', default='resources/affiliations_stripped.xml')
    parser.add_argument('--html', default='resources/affiliations_stripped.html')
    
    return parser.parse_args()

if __name__ == '__main__':

    args = get_args()

    process_files(args.xml, args.html)
