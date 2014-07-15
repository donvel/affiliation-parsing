import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
from operator import itemgetter

def get_list(ddict):
    return sorted(ddict.items(), key=itemgetter(1), reverse=True)

def parse(root):
    tags = defaultdict(lambda: [0, 0])
    tags_l2 = defaultdict(int) # These are only <sup> and <italic>

    for aff in root:
        local_tags = defaultdict(int)
        for item in aff:
            tags[item.tag][0] += 1
            local_tags[item.tag] += 1

            # Check nested tags
            for item2 in item:
                tags_l2[item2.tag] += 1
                for item3 in item2:
                    raise Exception("So deeeep")

        # Count repetitions
        for (key, val) in local_tags.items():
            if val > 1:
                tags[key][1] += 1


    tag_list = get_list(tags)
    
    #print tag_list
    return tag_list

if __name__ == '__main__':
    tree = ET.parse('../resources/affiliations.txt')
    root = tree.getroot()
    print "repeated: xx - present at least twice in xx affiliation entries"
    print "# of entries : " + str(len(list(root)))
    tl = parse(root)
    for (name, (nbr, rep)) in tl:
        print name + " : " + str(nbr) + ', repeated: ', str(rep)
