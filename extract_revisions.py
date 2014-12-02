import xml.etree.ElementTree as etree
import pickle
import gzip


def create_revision_list(xmL, topic_name):
    print "create_revision_list called..."

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
                    if num_revisions%10 == 0:
                        print "{} Revisions seen".format(num_revisions)
                    revisions.append(revision.find('{http://www.mediawiki.org/xml/export-0.8/}text').text)
                print title + '-->' + str(num_revisions)
                break
            x += 1
            if x%10 == 0:
                print "Document {} processed".format(x)
            elem.clear()

    #print 'Revisions: '
    #print revisions[1000]
    pickle.dump( revisions, gzip.open( "document_revisions.p", "wb" ) )
    return revisions


