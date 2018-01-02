#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
from multiprocess import Pool
import csv
import sys

from locids import loc_ids

req_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

base_url = 'https://neurotree.org/neurotree/'

def get_person(url):
    html = requests.get(url, headers=req_headers).content
    soup = BeautifulSoup(html, 'lxml')

    d = dict()
    d['url'] = url

    info = soup.find(class_='personinfo')

    d['name'] = info.find('h1').text.strip()

    info_rows = [x.strip().split(':') for x in info.text.split('\n')]
    area = [x[1].strip() for x in info_rows if x[0] == 'Area']
    if len(area) > 0:
        d['area'] = area[0]
    else:
        d['area'] = None

    table_rows = info.find_all('tr')

    for r in table_rows:
        text = r.text
        s = re.split('\xa0|\n', text)
        key = s[0].strip(' :').lower()
        values = [x for x in s[1:] if len(x) > 1]
        if key not in ['mean distance', 'affiliations']:
            continue
        if key == 'mean distance':
            try:
                d[key] = float(values[0])
            except:
                d[key] = None
        else:
            d[key] = ';'.join(values)

    connections = soup.find_all(class_='connection_list')

    parents = connections[0]
    rows = parents.find_all('tr')
    parent_list = []
    for r in rows:
        rr = [x.text.replace('\xa0', ' ') for x in r.find_all('td')]
        parent_list.append('|'.join(rr))
    d['parents'] = ';'.join(parent_list)

    children = connections[1]
    rows = children.find_all('tr')
    children_list = []
    for r in rows:
        rr = [x.text.replace('\xa0', ' ') for x in r.find_all('td')]
        children_list.append('|'.join(rr))
    d['children'] = ';'.join(children_list)

    return d

def get_person_try(url):
    try:
        return get_person(url)
    except AttributeError:
        return None


HEADER = ['name', 'area', 'affiliations', 'mean distance', 'parents', 'children', 'url']

people_urls = []

url_format = 'https://neurotree.org/neurotree/inst.php?locid={}'

for loc, loc_id in loc_ids.items():
    print(loc)
    url = url_format.format(loc_id)
    html = requests.get(url, headers=req_headers).content
    soup = BeautifulSoup(html, "lxml")

    rows = soup.find('tbody').find_all('tr')
    urls = [r.find('td').find('a').attrs['href'] for r in rows]
    urls = [base_url + person_url for person_url in urls]
 
    people_urls.extend(urls)
    print(len(urls))

scraped_urls = []
with open('neuroscience.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        scraped_urls.append(row['url'])

people_urls = set(people_urls) - set(scraped_urls)
people_urls = sorted(people_urls)

writer_f = open('neuroscience.csv', 'a')
writer = csv.DictWriter(writer_f, fieldnames=HEADER)
# writer.writeheader()

p = Pool(3)
results = p.imap_unordered(get_person_try, people_urls)

count = len(people_urls)

for i, person in enumerate(results):
    if person == None:
        continue
    
    print('\rprocessing person {}/{}'.format(i+1, count), end='')
    sys.stdout.flush()
    
    writer.writerow(person)
    writer_f.flush()

print('done!')
