import xml.etree.ElementTree as etree
import json

xmL = 'enwiki-20140203-pages-meta-history3.xml-p000053871p000055000'
x = 1

titles = {}
for event, elem in etree.iterparse(xmL, events=('start', 'end')):
    #print event, elem.tag
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.8/}page' and event == 'end':
        num_revisions = 0
        for revision in elem.iter('{http://www.mediawiki.org/xml/export-0.8/}revision'):
            num_revisions += 1
        title = elem.find('{http://www.mediawiki.org/xml/export-0.8/}title').text
        print title + '-->' + str(num_revisions)
        titles[title] = num_revisions
        x += 1
        elem.clear()

print x
with open('titles.json', 'w') as fp:
    fp.write(json.dumps(titles))
