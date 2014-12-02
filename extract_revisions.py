import xml.etree.ElementTree as etree


def create_revision_list(xmL, topic_name):

    x = 1

    revisions = []
    for event, elem in etree.iterparse(xmL, events=('start', 'end')):
        #print event, elem.tag
        if elem.tag == '{http://www.mediawiki.org/xml/export-0.8/}page' and event == 'end':
            num_revisions = 0
            title = elem.find('{http://www.mediawiki.org/xml/export-0.8/}title').text
            if title == topic_name:
                for revision in elem.iter('{http://www.mediawiki.org/xml/export-0.8/}revision'):
                    num_revisions += 1
                    revisions.append(revision.find('{http://www.mediawiki.org/xml/export-0.8/}text').text)
                print title + '-->' + str(num_revisions)
                break
            x += 1
            elem.clear()

    #print 'Revisions: '
    #print revisions[1000]

    return revisions

r = create_revision_list('enwiki-20140203-pages-meta-history3.xml-p000053871p000055000', 'The Empire Strikes Back')
