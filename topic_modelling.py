import nltk
import pickle
import gzip
import sys
import logging
import time
import extract_revisions as er
from nltk.corpus import *
from gensim import corpora,models,similarities


def preprocessing(revisions):
	print "preprocessing called..."
	corpus = []
	stop_words  = set(stopwords.words('english'))
	# punctuation = re.compile(r'[-.?!/,":;*()=%$\'/\\&_\[\]}{<>#^\-+@|0-9]')
	pattern = re.compile(r'\s\s+')
	punctuation = re.compile(r'[^a-zA-Z]+')
	third_layer = re.compile(r'(^| ).( |$)')
	# start_time = time.time()
	count = 0
	for each_revision in revisions:
		count = count +1
		try:
			punc_text = punctuation.sub(" ", each_revision)
			text = re.sub(pattern, ' ', punc_text) #to remove extra white spaces.
			third_text = re.sub(third_layer, ' ', text)  #to remove all other characters except for text
			tokenize = nltk.word_tokenize(third_text)
			lowered_text = [w.lower().strip() for w in tokenize] 
			text_without_stopwords = [w for w in lowered_text if not w in stop_words]
			# print text_without_stopwords
			corpus.append(text_without_stopwords)
			
			if count%100 == 0:
				print "Preprocessed {} revision".format(count)
		except:
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
	lsi.print_topics(2)
	print "Successful!"


def main():
	# revisions = er.create_revision_list('enwiki-20140203-pages-meta-history3.xml', 
		 # 'The Empire Strikes Back')
	start_time = time.time()
	# revisions = pickle.load(gzip.open("document_revisions.p", "rb" ))

	# print "\nNumber of revisions = ",len(revisions)
	
	# revisions_tokens = preprocessing(revisions)
	# print len(revisions_tokens)
	# print revisions_tokens

	# corpus_bow = corpus_create(revisions_tokens)
	corpus_bow = corpora.MmCorpus('wiki_en/revisions_bow.mm')

	tfidf = create_tfidf(corpus_bow)

	corpus_tfidf = tfidf[corpus_bow]
	
	print "Tfidf Corpus = ",len(corpus_tfidf)

	dictionary = corpora.Dictionary.load('wiki_en/revisions_tokens.dict')

	build_lsi(corpus_tfidf,dictionary)

	print "Total Execution time = {}".format(time.time() - start_time)



if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	main()
