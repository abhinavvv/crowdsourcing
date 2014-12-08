import nltk
import pickle
import gzip
import sys
import logging
import time
import json
import itertools
import extract_revisions as er
from nltk.corpus import *
from gensim import utils,corpora,models,similarities

RE_P0 = re.compile('<!--.*?-->', re.DOTALL | re.UNICODE) # comments
RE_P1 = re.compile('<ref([> ].*?)(</ref>|/>)', re.DOTALL | re.UNICODE) # footnotes
RE_P2 = re.compile("(\n\[\[[a-z][a-z][\w-]*:[^:\]]+\]\])+$", re.UNICODE) # links to languages
RE_P3 = re.compile("{{([^}{]*)}}", re.DOTALL | re.UNICODE) # template
RE_P4 = re.compile("{{([^}]*)}}", re.DOTALL | re.UNICODE) # template
RE_P5 = re.compile('\[(\w+):\/\/(.*?)(( (.*?))|())\]', re.UNICODE) # remove URL, keep description
RE_P6 = re.compile("\[([^][]*)\|([^][]*)\]", re.DOTALL | re.UNICODE) # simplify links, keep description
RE_P7 = re.compile('\n\[\[[iI]mage(.*?)(\|.*?)*\|(.*?)\]\]', re.UNICODE) # keep description of images
RE_P8 = re.compile('\n\[\[[fF]ile(.*?)(\|.*?)*\|(.*?)\]\]', re.UNICODE) # keep description of files
RE_P9 = re.compile('<nowiki([> ].*?)(</nowiki>|/>)', re.DOTALL | re.UNICODE) # outside links
RE_P10 = re.compile('<math([> ].*?)(</math>|/>)', re.DOTALL | re.UNICODE) # math content
RE_P11 = re.compile('<(.*?)>', re.DOTALL | re.UNICODE) # all other tags
RE_P12 = re.compile('\n(({\|)|(\|-)|(\|}))(.*?)(?=\n)', re.UNICODE) # table formatting
RE_P13 = re.compile('\n(\||\!)(.*?\|)*([^|]*?)', re.UNICODE) # table cell formatting
RE_P14 = re.compile('\[\[Category:[^][]*\]\]', re.UNICODE) # categories
RE_SECTIONS = re.compile('==[^=]+==$', re.UNICODE) # sections 

def remove_markup(text):
    text = re.sub(RE_P2, "", text) # remove the last list (=languages)
    # the wiki markup is recursive (markup inside markup etc)
    # instead of writing a recursive grammar, here we deal with that by removing
    # markup in a loop, starting with inner-most expressions and working outwards,
    # for as long as something changes.
    iters = 0
    while True:
        old, iters = text, iters + 1
        text = re.sub(RE_P0, "", text) # remove comments
        text = re.sub(RE_P1, '', text) # remove footnotes
        text = re.sub(RE_P9, "", text) # remove outside links
        text = re.sub(RE_P10, "", text) # remove math content
        text = re.sub(RE_P11, "", text) # remove all remaining tags
        # remove templates (no recursion)
        text = re.sub(RE_P3, '', text)
        text = re.sub(RE_P4, '', text)
        text = re.sub(RE_P14, '', text) # remove categories
        text = re.sub(RE_P5, '\\3', text) # remove urls, keep description
        text = re.sub(RE_P7, '\n\\3', text) # simplify images, keep description only
        text = re.sub(RE_P8, '\n\\3', text) # simplify files, keep description only
        text = re.sub(RE_P6, '\\2', text) # simplify links, keep description only
        # remove table markup
        text = text.replace('||', '\n|') # each table cell on a separate line
        text = re.sub(RE_P12, '\n', text) # remove formatting lines
        text = re.sub(RE_P13, '\n\\3', text) # leave only cell content
        # remove empty mark-up
        text = text.replace('[]', '')
        if old == text or iters > 2: # stop if nothing changed between two iterations or after a fixed number of iterations
            break

    # the following is needed to make the tokenizer see '[[socialist]]s' as a single word 'socialists'
    # TODO is this really desirable?
    text = text.replace('[', '').replace(']', '') # promote all remaining markup to plain text
    return text


def preprocessing(revisions):
	print "preprocessing called..."
	corpus = []
	stop_words  = set(stopwords.words('english'))
	punctuation = re.compile(r'[-.?!/,":;*()=%$\'/\\&_\[\]}{<>#^\-+@|0-9]')
	pattern = re.compile(r'\s\s+')
	punctuation = re.compile(r'[^a-zA-Z]+')
	third_layer = re.compile(r'(^| ).( |$)')
	# # start_time = time.time()
	count = 0
	for each_revision in revisions:
		try:
			count = count +1
			text = utils.decode_htmlentities(utils.to_unicode(each_revision, 'utf8', errors='ignore'))
    		# text = utils.decode_htmlentities(text)
			punc_text = punctuation.sub(" ", remove_markup(text))
			text = re.sub(pattern, ' ', punc_text) #to remove extra white spaces.
			third_text = re.sub(third_layer, ' ', text)  #to remove all other characters except for text
			tokenize = nltk.word_tokenize(third_text)
			lowered_text = [w.lower().strip() for w in tokenize] 
			text_without_stopwords = [w for w in lowered_text if not w in stop_words]
			# # print text_without_stopwords
			corpus.append(text_without_stopwords)
			if count%100 == 0:
				print "Preprocessed {} revision".format(count)
		except:
			sys.exc_info()[0]
			next 
        	
  	print len(corpus)
	return corpus

def corpus_create(revisions_tokens):
	print "corpus_create called.."
	dictionary = corpora.Dictionary(revisions_tokens)
	dictionary.save('wiki_en/revisions_tokens.dict')
	print(dictionary)
	print len(revisions_tokens)
	corpus = [dictionary.doc2bow(text) for text in revisions_tokens]
	corpora.MmCorpus.serialize('wiki_en/revisions_bow.mm',corpus)
	print "Bow Corpus = ",len(corpus)
	return corpus

def create_tfidf(corpus):
	print "create_tfidf called..."
	corpus_tfidf = models.TfidfModel(corpus)
	corpus_tfidf.save('wiki_en/revisions_tfidf.tfidf_model')
	return corpus_tfidf


def build_lsi(corpus_tfidf,dictionary,no_of_topics=10):
	print "build_lsi called ..."
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
	lsi.save('wiki_en/revisions_lsi.lsi')
	corpus_lsi = lsi[corpus_tfidf]
	
	# lsi.print_topics(2)
	print "Successful!"
	return lsi


def main():
	revisions = er.create_revision_list('enwiki-20140203-pages-meta-history3.xml', 
		 'The Empire Strikes Back')
	
	# revisions = pickle.load(gzip.open("document_revisions.p", "rb" ))

	print "\nNumber of revisions = ",len(revisions)
	
	revisions_tokens = preprocessing(revisions)
	
	print "\nNumber of edits = ", len(revisions_tokens)
	



	corpus_bow = corpus_create(revisions_tokens)

	print len(corpus_bow)

	# tfidf = models.TfidfModel.load('wiki_en/revisions_tfidf.tfidf_model')
	# print "\n ----------------------------------"
	# print "\n The tfidf model is = ",tfidf

	
	tfidf = create_tfidf(corpus_bow)

	corpus_tfidf = tfidf[corpus_bow]



	dictionary = corpora.Dictionary.load('wiki_en/revisions_tokens.dict')

	lsi = build_lsi(corpus_tfidf,dictionary,40)
	# # lsi = build_lsi(corpus_tfidf,dictionary)
	# lsi = models.LsiModel.load('wiki_en/revisions_lsi.lsi')


	# print "\n ----------------- LSI MODEL ---------------------"
	
	# print lsi

	print "\n ------------ TOP 10 TOPICS -----------------------"
	lsi.print_topics(10)
	
	# corpus_lsi = lsi[corpus_tfidf]

	# print " \n -------------- Computing similarities ---------------"
	# index = similarities.MatrixSimilarity(corpus_lsi)
	# index.save('wiki.index')
	# index = similarities.MatrixSimilarity.load('wiki.index')
	# # print corpus_lsi
	# test = lsi[corpus_bow[1000]]
	# sims = index[test]  
	# print "Similarities of 100 = {}, 1000 = {}, 4000 = {}".format(sims[100],sims[1000],sims[4000])
	# # print(list(enumerate(sims)))  




	# print "Total Execution time = {}".format(time.time() - start_time)



if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	main()
