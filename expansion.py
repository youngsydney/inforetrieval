from collections import OrderedDict
from operator import itemgetter
import math
from PyDictionary import PyDictionary
import time



def RF_idf(score, terms_by_doc, terms_idf, query_terms, query):
	"""This function selects good terms to expand the query from the top N 
	documents and using a the top M terms. It selects good terms as a combintation
	of idf and the num of top N documents the term is found in."""

	M = 2
	X = 2
	count = 0

	good_terms = []
	candidates = {}
	to_sort_cand = {}

	sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))

	for idx, doc in enumerate(sorted_scores):
		if idx<M:
			for term in terms_by_doc[doc]:
				if term in candidates:
					candidates[term]['docCount'] +=1
				else:
					candidates[term] = {'docCount':1}

	for term in candidates:
		to_sort_cand[term] = (candidates[term]['docCount'] * terms_idf[term])

	sorted_candidates = OrderedDict(sorted(to_sort_cand.items(), key=itemgetter(1), reverse=True))

	for idx, term in enumerate(sorted_candidates):
		if count<X and term not in query_terms:
			good_terms.append(term)
			count += 1

	new_query = query
	for term in good_terms:
		new_query += (' ' + term)

	return new_query

def RF_idf_tf(score, lexicon, terms_by_doc, terms_idf, query_terms, query):
	"""This function expands the query using relevance feedback. It selects the 
	good terms from the top N documents using the top M terms. It selects good terms
	as a combintation of idf and term frequency in the top N documents."""

	M = 4
	X = 3
	count = 0

	good_terms = []
	candidates = {}
	to_sort_cand = {}

	sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))

	for idx, doc in enumerate(sorted_scores):
		if idx<M:
			for term in terms_by_doc[doc]:
				if term in candidates:
					candidates[term]['tf'] += lexicon[term][doc]
				else:
					candidates[term] = {'tf':lexicon[term][doc]}

	for term in candidates:
		to_sort_cand[term] = (candidates[term]['tf'] * terms_idf[term])

	sorted_candidates = OrderedDict(sorted(to_sort_cand.items(), key=itemgetter(1), reverse=True))

	for idx, term in enumerate(sorted_candidates):
		if count < X and term not in query_terms:
			good_terms.append(term)
			count += 1
	new_query = query
	for term in good_terms:
		new_query += (' ' + term)

	return new_query


def find_synonyms(query_terms, query, terms_idf):
	"""This function finds synonyms for a query. Then it selects
	the best X synonyms based on their idf."""

	synonyms = {}
	dictionary=PyDictionary()
	for term in query_terms:
		syn = dictionary.synonym(term)
		if syn:
			for word in syn:
				if word.encode("utf-8") in terms_idf:
					synonyms[word.encode("utf-8")] = terms_idf[word.encode("utf-8")]
		else:
			pass
	sorted_syns = OrderedDict(sorted(synonyms.items(), key=itemgetter(1), reverse=True))
	X = 1

	new_query = query
	for idx, term in enumerate(sorted_syns):
		if idx<X:
			new_query += (' ' + term)

	return new_query


