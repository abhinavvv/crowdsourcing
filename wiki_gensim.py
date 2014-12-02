import logging, gensim, bz2,sys
from collections import Counter
from gensim import corpora, models, similarities
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# load id->word mapping (the dictionary), one of the results of step 2 above
id2word = gensim.corpora.Dictionary.load_from_text('wiki_en/_wordids.txt.bz2')
print "----------- id2word -------------"
print id2word
print "-------- bow -----------"
corpus = gensim.corpora.MmCorpus('wiki_en/_bow.mm')
counter_list = Counter([ item for sublist in corpus for item in sublist ]).most_common()
for key,value in counter_list:
	print id2word[key[0]], key[1], value


sys.exit()
print "------- tf_idf -------------"

# # load corpus iterator
tf_idf = gensim.corpora.MmCorpus('wiki_en/_tfidf.mm')
print tf_idf
sys.exit()
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
# mm = gensim.corpora.MmCorpus(bz2.BZ2File('_tfidf.mm.bz2')) # use this if you compressed the TFIDF output (recommended)

# print(mm)

lsi = gensim.models.lsimodel.LsiModel(corpus=tf_idf, id2word=id2word,num_topics=1000)
# lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100, update_every=0, passes=1)


# print "\n\n $$$$$$$$$$$$$$ LSI $$$$$$$$$$$$$$\n \n"
# print "--------------------"
# print lsi.print_topic(1)
# print "--------------------"
# print lsi.show_topic(1)
for key,value in id2word.iteritems():
	print key, value

print len(set(id2word.values()))
# print len(lsi.print_topics())

# corpus_lsi = lsi[corpus_tfidf]
# for topic in corpus_lsi:
# 	print 


# print "\n\n $$$$$$$$$$$$$$ LDA $$$$$$$$$$$$$$\n \n"

# lda.print_topics(10)

# mm = gensim.corpora.MmCorpus("wiki_en/_bow.mm.index")
# words = {}

# for doc in mm:
# 	for features in doc:
# 		word = features[0]
# 		tf_idf = features[1]
# 		words[word] = list(tf_idf) if word not in words.keys() else words[word].append(tf_idf)
# 		print id2word[features[0]],
# 	print "---------"

