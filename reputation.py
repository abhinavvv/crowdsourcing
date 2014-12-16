import nltk
import pickle
import gzip
import sys
import logging, gensim, bz2
import time
import json
import itertools
import math
import extract_revisions as er
from nltk.corpus import *
from gensim import utils, corpora, models, similarities
import xml.etree.ElementTree as etree
from collections import Counter
import difflib
import numpy as np
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


xml = 'enwiki-20140203-pages-meta-history3.xml-p000053871p000055000'
topic_name = 'The Empire Strikes Back'
a = []                                                                                              # Author(edit)
r_lsi = {}                                                                              # Reputation(Author) using lsi
r_bow = {}                                                                              # Reputation(Author) using bow
r_wdiff = {}                                                                            # Reputation(Author)using wdiff
r_euclidean = {}                                                                        # Reputation(Author) using euclidean distance between topics


K = 5                                                                   # Number of furure revisions to compare against
epsilon = 0.1  
alpha = 0.5     
revisions = pickle.load(gzip.open( "document_revisions.p", "rb" ))                                                    # effect of new users
corpus_bow = corpora.MmCorpus('wiki_en/revisions_bow.mm')                                           # Bow Corpus
# lsi = models.LsiModel.load('wiki_en/revisions_lsi_50.lsi')                                                  # LSI Model
# lsi.print_topics(10)
# index_lsi = similarities.MatrixSimilarity.load('wiki_en/wiki_50.index')                                     # LSI index
# index_bow = similarities.MatrixSimilarity.load('wiki_en/wiki_bow.mm.index')                            # BOW index


def create_a():
    for event, elem in etree.iterparse(xml, events=('start', 'end')):
        if elem.tag == '{http://www.mediawiki.org/xml/export-0.8/}page' and event == 'end':
            title = elem.find('{http://www.mediawiki.org/xml/export-0.8/}title').text
            if title == topic_name:
                print 'Found ', topic_name
                n = 0
                for revision in elem.iter('{http://www.mediawiki.org/xml/export-0.8/}revision'):
                    contributor = revision.find('{http://www.mediawiki.org/xml/export-0.8/}contributor')
                    user_name = contributor[0].text
                    a.append(user_name)
                    n += 1
                print n
                with open('a.pik', 'wb') as pk:
                    pickle.dump(a, pk)
                break
            elem.clear()


def load_a():
    with open('wiki_en/a.pik', 'rb') as pk:
        return pickle.load(pk)


def distance_topics(x, y):
    y = corpus_bow[y]
    y = lsi[y]
    sims = index_lsi[y]
    return sims[x]


def distance_cosine(x, y):
    y = corpus_bow[y]
    sims = index_bow[y]
    return sims[x]

def eucledian_topics(x,y):
    return np.linalg.norm(np.array(lsi[corpus_bow[x]])-np.array(lsi[corpus_bow[y]]))



def distance_wdiff(x,y):
    a = revisions[x]
    b = revisions[y]
    changes =  list(difflib.ndiff(a.split(), b.split()))
    additions = [string for string in changes if string.startswith('+')]
    removals = [string for string in changes if string.startswith('-')]
    return len(additions) + len(removals)

def quality(d1k,d2k,d12):
    return float(d1k - d2k)/d12

def f(reput_score):
    return math.log(1 + max(0, epsilon + reput_score))

# Abhinav: add your two distances measures here

#create_a()
a = load_a()

                                                                                            # delete problamatic indices
print '---------deleting----------'
del a[2472]
del a[3080]
del revisions[2472]
del revisions[3080]
print 'Length of a: ', len(a)

print "number of unique authors: ", len(set(a))


for user in set(a):                                                                              # Initialize reputation
    r_lsi[user] = 0
    r_bow[user] = 0
    r_wdiff[user] = 0
    r_euclidean[user] = 0

i = 0
count = 0
print "number of revisions = ", len(revisions)
print "length of bow = ",len(corpus_bow)
for edit in corpus_bow:
    try:
        if count %10 == 0:
            print " {} Iterations done  ".format(count) 
        count = count + 1
        if i == 0:
            next
        # d12_bow = distance_cosine(i-1, i)
        # d12_lsi = distance_topics(i-1, i)
        d12_wdiff = distance_wdiff(i-1, i)

        # Abhinav: add your two distance measures here
        user = a[i]
        n = 0
        j = i+1
        add = 0
        while n < K:
            # print n
            if a[j] == a[i]:
                j += 1
                next
            # d2k_lsi = distance_topics(j, i)
            # d1k_lsi = distance_topics(j, i-1)
            d1k_wdiff = distance_wdiff(j,i-1 )
            d2k_wdiff = distance_wdiff(j, i)
            # q_lsi = quality(d1k_lsi, d2k_lsi, d12_lsi)
            # q_bow = quality(d1k_bow, d2k_bow, d12_bow)
            q_wdiff = quality(d1k_wdiff, d2k_wdiff, d12_wdiff)
            add += (1-alpha)*math.pow(alpha,((i-j)+1))*(q_wdiff * d12_wdiff * f(r_wdiff[a[j]]))
            n = n+1
            j = j + 1
        r_wdiff[a[i]] = r_wdiff[a[i]] + add 
        print "Author = {}  Reputation score = {} ".format(a[i], r_wdiff[a[i]])
        i = i+1
    except:
        i = i+1
        next


pickle.dump( r_wdiff, gzip.open( "wdiff_reputation", "wb" ) )
pickle.dump( a, gzip.open( "author.p", "wb" ) )

#         # call quality formula using
