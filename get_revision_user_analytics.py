import xml.etree.ElementTree as etree
from collections import Counter
xml = 'enwiki-20140203-pages-meta-history3.xml-p000053871p000055000'
topic_name = 'The Empire Strikes Back'
data = {}


for event, elem in etree.iterparse(xml, events=('start', 'end')):
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.8/}page' and event == 'end':
        title = elem.find('{http://www.mediawiki.org/xml/export-0.8/}title').text
        if title == topic_name:
            print 'Found ', topic_name
            for revision in elem.iter('{http://www.mediawiki.org/xml/export-0.8/}revision'):
                contributor = revision.find('{http://www.mediawiki.org/xml/export-0.8/}contributor')
                user_name = contributor[0].text
                if user_name in data.keys():
                    data[user_name] += 1
                else:
                    data[user_name] = 1
            break
        elem.clear()

c = Counter(data.values())
sums = 0
for x, y in c.iteritems():
    sums += int(x)*y
print sums