#!/usr/bin/env python

import csv
from collections import Counter, defaultdict
from pprint import pprint

reader_f = open('neuroscience.csv', 'r')
reader = csv.DictReader(reader_f)

people = []

for row in reader:
    person = dict(row)

    children = []
    for child in row['children'].split(';'):
        if child == '':
            continue
        x = child.split('|')
        if len(x) != 4 \
           or x[1] not in ['grad student', 'post-doc'] \
           or x[-1] == '':
            continue
        children.append(x)

    if len(children) == 0:
        person['place'] = None
    else:
        person['place'] = children[-1][-1]

    parents = []
    for parent in row['parents'].split(';'):
        if parent == '':
            continue
        x = parent.split('|')
        if len(x) != 4 \
           or x[1] not in ['grad student'] \
           or x[3] == '':
            continue
        parents.append(x)

    if len(parents) == 0:
        person['phd'] = None
    else:
        person['phd'] = parents[-1][-1]

    parents = []
    for parent in row['parents'].split(';'):
        if parent == '':
            continue
        x = parent.split('|')
        if len(x) != 4 \
           or x[1] not in ['post-doc'] \
           or x[3] == '':
            continue
        parents.append(x)

    if len(parents) == 0:
        person['post-doc'] = None
    else:
        person['post-doc'] = parents[-1][-1]

        
    people.append(person)
 
counts = defaultdict(int)

for person in people:
    # phd = person['post-doc'] # for post-doc rates
    phd = person['phd']
    place = person['place']
    if phd == None:
        continue

    if place == None:
        counts[(phd.strip(), 'justphd')] += 1
        continue
    
    # else:
    counts[(phd.strip(), 'phd')] += 1
    counts[(place.strip(), 'place')] += 1

colleges = set([k[0] for k in counts.keys()])

ratios = []
for c in colleges:
    if counts[(c,'phd')] >= 20:
        ratio = (counts[(c,'phd')])/(counts[(c, 'phd')] + counts[(c, 'place')] + counts[(c, 'justphd')])
        ratios.append((c, ratio, counts[(c, 'phd')], counts[(c, 'place')], counts[(c, 'justphd')]))

ratios = sorted(ratios, key=lambda x: -x[1])

header = ['Institution', 'Ratio', 'PhD placed', 'PhD unclear', 'Professors at institution']
print('|' + '|'.join(header)+ '|')
print('|' + '|'.join(['-' for _ in header]) + '|')
for row in ratios:
    row = list(row)
    row[1] = '{:.3f}'.format(row[1])
    row = [str(r) for r in row]
    print('|' + '|'.join(row) + '|')
