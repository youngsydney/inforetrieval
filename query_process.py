import preprocess
import output
import math
import time
import re 
import constant
from collections import OrderedDict
from operator import itemgetter
import commands
from texttable import Texttable
import expansion
import reduction


def report_1(s_lexicon, s_term_list, st_lexicon, st_term_list, queries, query_start):
	"""This report runs processing of the queries against the BM25, 
	dirichlet, and VSM models."""

	models = ['bm25', 'vsm', 'dirichlet']
	indexes = ['single', 'stem']
	data = {'vsm':{}, 'bm25':{}, 'dirichlet':{}}

	for index in indexes:
		for mdl in models:
			query_start = time.time()
			with open("results.txt", 'w') as resultsFile:
				for queryID in sorted(queries):
					score = {}
					query_terms = query_lexicon(queries[queryID], index)
					if index == 'single':
						score = Q_Score(mdl, query_terms, s_lexicon, s_term_list, queryID, score, index)
					elif index == 'stem':
						score = Q_Score(mdl, query_terms, st_lexicon, st_term_list, queryID, score, index)
					sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
					for idx, doc in enumerate(sorted_scores):
						if idx<100:
							resultsFile.write(queryID + ' ' + '0 ' + doc + ' ' + str(idx+1) + ' ' + str(sorted_scores[doc]) + ' ' + mdl + '\n')
			query_end = time.time()
			data[mdl][(index + '_QPT')]=str(query_end-query_start)

			status, output = commands.getstatusoutput("./trec_eval -m map  qrel.txt results.txt")
			if status == 0:
				output = output.replace('\t', ' ')
				MAP = output.split('all ')[1]
				data[mdl][(index + '_MAP')] = MAP
			else:
				data[mdl][(index + '_MAP')] = 'error'
			score.clear()
	return data 


def Q_Score(model, query_terms, lexicon, term_list, queryID, score, index_type):
	"""This function is a helper to report 1(), it calls the correct 
	model to process the query."""

	if model == 'vsm':
		score = VSM_Score(query_terms, lexicon, term_list)
	elif model == 'bm25':
		score = BM25_Score(query_terms, lexicon, term_list, queryID, score, index_type)
	elif model == 'dirichlet':
		score = Dirichlet_Score(query_terms, lexicon)
	return score


def report_2(st_lexicon, st_term_list, p_lexicon, p_term_list, po_lexicon, po_term_list, queries, query_start):
	"""This report runs report 2 -- first sending against the phrase or positional index 
	and then sending against the stem if not enough documents found."""

	data = {'MAP':'', 'QPT': ''}
	index_count = {'phrase': 0, 'positional': 0}

	with open("results.txt", 'w') as resultsFile:
		for queryID in sorted(queries):
			query_terms = query_lexicon(queries[queryID], 'phrase')
			index_decision = makeDecision(query_terms, p_term_list)
			index_count[index_decision] += 1

			query_terms = query_lexicon(queries[queryID], index_decision)

			score = {}
			if index_decision == 'phrase':
				score = BM25_Score(query_terms, p_lexicon, p_term_list, queryID, score, 'phrase')
			elif index_decision == 'positonal':
				score = BM25_Score(query_terms, po_lexicon, po_term_list, queryID, score, 'positional')

			if len(score) < 99:
				query_terms = query_lexicon(queries[queryID], 'stem')
				score = BM25_Score(query_terms, st_lexicon, st_term_list, queryID, score, 'stem')

			sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
			for idx, doc in enumerate(sorted_scores):
				if idx<100:
					resultsFile.write(queryID + ' ' + '0 ' + doc + ' ' + str(idx+1) + ' ' + str(sorted_scores[doc]) + ' ' + 'phrase_stem '  + '\n')
	query_end = time.time()
	data['QPT'] = str(query_end-query_start)

	status, output = commands.getstatusoutput("./trec_eval -m map qrel.txt results.txt")
	output = output.replace ('\t', ' ')
	MAP = output.split('all ')[1]
	data['MAP'] = MAP

	return index_count, data



def query_input(query_file):
	"""This function reads the query file and stores the
	different queries (title, desc, narrative)."""

	finalQueries = {}

	with open(query_file, 'r') as queryFile:
		wholeFile = queryFile.read()
		wholeFile = wholeFile.replace('</top>', '</top> BREAK_NEW_QUERY')
		queries = wholeFile.split('BREAK_NEW_QUERY')

	for query in queries:
		if "Number:" not in query:
			break
		query = query.replace('\n', ' ')
		ID = re.search(constant.query_ID, query)
		if ID:
			queryID = ID.group(1)
		t = re.search(constant.query_title, query)
		if t:
			title = t.group(1)
		d = re.search(constant.query_desc, query)
		if d:
			desc = d.group(1)
		n = re.search(constant.query_narr, query)
		if n:
			narr = n.group(1)
		finalQueries[queryID] = {"title":title, "desc":desc, "narr":narr}
	return finalQueries


def query_lexicon(query, index_type):
	"""This function builds an index of the
	term weights for the query terms. """

	if index_type != 'None':
		terms = preprocess.processing(query, index_type)
	else:
		terms = query
	query_terms = {}

	for term in terms:
		if term in query_terms:
			query_terms[term] += 1
		else:
			query_terms[term] = 1
	
	return query_terms


def build_document_index(index):
	"""This function builds diction of {docID: [terms in doc]}"""
	num_docs=0
	terms_by_document={}

	for term in index:
		for docID in index[term]:
			if docID in terms_by_document:
				terms_by_document[docID].append(term)
			else:
				terms_by_document[docID]=[term]
				num_docs +=1
	return terms_by_document, num_docs


def makeDecision(query_terms, p_term_list):
	"""This function decides whether to send a 
	query to the phrase or positional index."""

	index_decision = ''

	sum_df = 0
	num_phrases = 0

	for phrase in query_terms:
		if phrase in p_term_list:
			sum_df += p_term_list[phrase]
			num_phrases += 1

	if num_phrases == 0 or sum_df == 0:
		return 'positional'
	else:	
		average_df = float(sum_df) / num_phrases

	if average_df > 1:
		index_decision = 'phrase'
	else:
		index_decision = 'positional'

	return index_decision 



"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR VSM COSINE"""

def VSM_Score(query_terms, index, term_list):
	"""The main driver function for the VSM COSINE
	retrieval model. Builds the dictionary of scores."""

	vsm_score = {}
	dict_term_weights = {}

	terms_by_doc, num_docs = build_document_index(index)
	terms_idf = VSM_idf(term_list, num_docs)

	query_termWeights = VSM_query_termWeight(terms_idf, index, query_terms)

	for term in query_terms:
		if term in index:
			query_term_posting_list = index[term]

			for docID in query_term_posting_list:
				if docID not in dict_term_weights:
					dict_term_weights = VSM_termWeight(docID, terms_idf, index, terms_by_doc[docID], dict_term_weights)

				if docID not in vsm_score:
					vsm_score[docID] = query_termWeights[term] * dict_term_weights[docID][term]
				else:
					vsm_score[docID] += query_termWeights[term] * dict_term_weights[docID][term]
		else:
			pass

	for docID in vsm_score:
		vsm_score[docID] = vsm_score[docID] / math.sqrt(pow(VSM_sum_termWeights_doc(dict_term_weights, docID),2)*pow(VSM_sum_termWeights_query(query_termWeights), 2))

	return vsm_score


def VSM_idf(term_list, num_docs):
	"""This function precalculates all the term idfs."""

	terms_idf={}
	for term in term_list:
		terms_idf[term]=math.log10((float(num_docs)/term_list[term]))

	return terms_idf


def VSM_termWeight_numerator(term_idf, termFreq):
	"""This function calculates the numerator of the 
	term weight for a term in a document."""

	weight = 0
	weight = (math.log(termFreq)+1)*term_idf

	return weight


def VSM_termWeight(docID, terms_idf, index, terms_in_docID, dict_term_weights):
	"""This function calculates all the term weights for terms
	in a specific document."""

	sum_termWeights_docID = 0
	for term in terms_in_docID:
		if docID not in dict_term_weights:
			dict_term_weights[docID] = {term:VSM_termWeight_numerator(terms_idf[term], index[term][docID])}
		else:
			dict_term_weights[docID][term] = VSM_termWeight_numerator(terms_idf[term], index[term][docID])
		sum_termWeights_docID += dict_term_weights[docID][term]

	for term in dict_term_weights[docID]:
		dict_term_weights[docID][term] = dict_term_weights[docID][term] / sum_termWeights_docID

	return dict_term_weights


def VSM_sum_termWeights_doc(dict_term_weights, docID):
	"""This calculates the sum of the term
	weights for a given document."""

	sum_weights=0
	for term in dict_term_weights[docID]:
		sum_weights += dict_term_weights[docID][term]

	return sum_weights


def VSM_sum_termWeights_query(query_termWeights):
	"""This is the sum of the term weights in the query."""

	sum_weights=0
	for term in query_termWeights:
		sum_weights += query_termWeights[term]

	return sum_weights


def VSM_query_termWeight(terms_idf, index, query_terms):
	"""This is the function that builds the term weights
	of the query terms."""

	sum_termWeights_query = 0
	dict_query_termWeights = {}

	for term in query_terms:
		if term in terms_idf:
			dict_query_termWeights[term] = VSM_termWeight_numerator(terms_idf[term], query_terms[term])
		else:
			dict_query_termWeights[term] = VSM_termWeight_numerator(1, query_terms[term])
		sum_termWeights_query += dict_query_termWeights[term]

	for term in dict_query_termWeights:
		dict_query_termWeights[term] = dict_query_termWeights[term] / sum_termWeights_query

	return dict_query_termWeights



"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR BM-25"""

def BM25_Score(query_terms, index, term_list, queryID, score, indexType):
	"""This is the main function which produces the BM25 score."""

	if indexType == 'positional':
		score = BM25_Score_Positional(query_terms, index, term_list, queryID, score)
		return score
	k1 = 1.2
	k2 = 1000
	b = 0.75

	document_lengths, average_length, num_docs = build_BM25_document_lengths(index)
	for term in query_terms:
		if term in index:
			term_weight = BM25_weight(term_list, term, num_docs)
			B = ((k2 + 1) * query_terms[term]) / float(k2 + query_terms[term])
			query_term_posting_list = index[term]

			for docID in query_term_posting_list:
				A = ((k1 + 1) * index[term][docID]) / float(index[term][docID] + k1 * (1 - b + b * (document_lengths[docID] / average_length)))
				if docID not in score:
					score[docID] = term_weight * A * B 
				else:
					score[docID] += term_weight * A * B 
		else:
			pass

	return score


def BM25_Score_Positional(query_terms, index, term_list, queryID, score):
	"""This is the BM25 for the positional index, as the positional
	does not have tf but the positions stored so has to 
	be processed slightly differently."""

	k1 = 1.2
	k2 = 500
	b = 0.75

	document_lengths, average_length, num_docs = build_BM25_document_lengths(index)
	for term in query_terms:
		if term in index:
			term_weight = BM25_weight(term_list, term, num_docs)
			B = ((k2 + 1) * query_terms[term]) / float(k2 + query_terms[term])
			query_term_posting_list = index[term]

			for docID in query_term_posting_list:
				A = ((k1 + 1) * len(index[term][docID])) / float(len(index[term][docID]) + k1 * (1 - b + b * (document_lengths[docID] / average_length)))
				if docID not in score:
					score[docID] = term_weight * A * B 
				else:
					score[docID] += term_weight * A * B 
		else:
			pass

	
	return score


def BM25_weight(term_list, term, num_docs):
	"""This function precalculates all the term idfs, which for BM-25 
	is the weight of the term."""

	term_weight = math.log((num_docs-term_list[term]+0.5)/(term_list[term]+0.5))

	return term_weight


def build_BM25_document_lengths(index):
	"""This function builds diction of {docID: num_terms_in_doc}"""

	sum_doc_lengths = 0
	num_docs = 0
	document_lengths = {}

	for term in index:
		for docID in index[term]:
			sum_doc_lengths += index[term][docID]
			if docID in document_lengths:
				document_lengths[docID] += index[term][docID]
			else:
				document_lengths[docID] = index[term][docID]
				num_docs += 1
	average_length = float(sum_doc_lengths) / num_docs

	return document_lengths, average_length, num_docs



"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR Dirichlet Smoothing"""

def Dirichlet_Score(query_terms, index):
	"""This is the function which produces
	the Dirichlet score."""

	dirichlet_score = {}
	doc_numerator_value = 0 
	doc_denominator_value = 0
	miu = 0
	# |C| num terms in the entire collection 

	document_lengths, average_length, collection_length = build_Dirichlet_doc_collection_length(index)
	tf_collection = build_tf_in_collection(index)
	miu = 500

	for term in query_terms:
		if term in index: 
			query_term_posting_list = index[term]
			for docID in query_term_posting_list:

				numerator = index[term][docID] + ((miu * float(tf_collection[term])) / collection_length)
				denominator = document_lengths[docID] + miu 

				if docID not in dirichlet_score:
					#dirichlet_score[docID] = math.log((float(numerator) / denominator))
					dirichlet_score[docID] = (float(numerator) / denominator)
				else:
					#dirichlet_score[docID] += math.log((float(numerator) / denominator))
					dirichlet_score[docID] = (float(numerator) / denominator)
		else:
			pass

	return dirichlet_score


def build_Dirichlet_doc_collection_length(index):
	"""This function builds the document 
	lengths for all the documents in the collection."""

	collection_length = 0
	num_docs = 0
	document_lengths = {}

	for term in index:
		for docID in index[term]:
			collection_length += index[term][docID]
			if docID in document_lengths:
				document_lengths[docID] += index[term][docID]
			else:
				document_lengths[docID] = index[term][docID]
				num_docs += 1
	average_length = float(collection_length) / num_docs

	return document_lengths, average_length, collection_length

def build_tf_in_collection(index):
	"""This function builds the collection 
	frequency for all the terms in the collection. """

	tf_collection = {}

	for term in index:
		for docID in index[term]:
			if term in tf_collection:
				tf_collection[term] += index[term][docID]
			else:
				tf_collection[term] = index[term][docID]

	return tf_collection




"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING with EXPANSION OR REDUCTION"""

def assign_description(ty, data):
	"""This assigns the description to the type to be used in the final output
	for project 3."""

	if ty == 'control_title':
		data[ty]['explanation'] = 'Control -- processing with title queries'
	elif ty == 'control_desc':
		data[ty]['explanation'] = 'Control -- processing with description queries'
	elif ty == 'control_narr':
		data[ty]['explanation'] = 'Control -- processing with narr queries'
	elif ty == 'RF_numDocs':
		data[ty]['explanation'] = 'Expansion -- Top 2 Docs, Top 2 terms, chosen by idf * num docs'
	elif ty == 'RF_freqT':
		data[ty]['explanation'] = 'Expansion -- Top 4 Docs, Top 3 terms, chosen by tf in top docs * idf'
	elif ty == 'exp_Thesaurus':
		data[ty]['explanation'] = 'Expansion -- added 1 term from machine readable thesaurus'
	elif ty == 'partial_Percent':
		data[ty]['explanation'] = 'Reduction -- Partial query processing by selecting 72 percent of query terms, highest by idf * tf in query'
	elif ty == 'partial_Number':
		data[ty]['explanation'] = 'Reduction -- Partial query processing by selecting 16 query terms, highest by idf * tf in query'

	return data


def get_query(ty, queries, s_lexicon, s_term_list, queryID, score, index, terms_idf, terms_by_doc):
	"""This function is used for query reduction and expansion in Project 3. It returns the query_terms according to the
	type it is in charge of -- so involve relevance feedback, or partial processing, or jsut regular query term processing."""

	queries_title = {}
	queries_desc = {}
	queries_narr = {}
	score = {}

	for ID in queries:
		queries_title[ID] = queries[queryID]['title']
		queries_desc[ID] = queries[queryID]['desc']
		queries_narr[ID] = queries[queryID]['narr']

	if ty == 'control_title':
		new_query = queries_title[queryID]
	elif ty == 'control_desc':
		new_query = queries_desc[queryID]
	elif ty == 'control_narr':
		new_query = queries_narr[queryID]
	elif ty == 'RF_numDocs':
		query_terms = query_lexicon(queries_title[queryID], index)
		score = send_to_SE('vsm', query_terms, s_lexicon, s_term_list, queryID, score, index)
		new_query = expansion.RF_idf(score, terms_by_doc, terms_idf, query_terms, queries_title[queryID])
	elif ty == 'RF_freqT':
		query_terms = query_lexicon(queries_title[queryID], index)
		score = send_to_SE('vsm', query_terms, s_lexicon, s_term_list, queryID, score, index)
		new_query = expansion.RF_idf_tf(score, s_lexicon, terms_by_doc, terms_idf, query_terms, queries_title[queryID])
	elif ty == 'exp_Thesaurus':
		query_terms = query_lexicon(queries_title[queryID], index)
		new_query = expansion.find_synonyms(query_terms, queries_title[queryID], terms_idf)
	elif ty == 'partial_Percent':
		query_terms = query_lexicon(queries_narr[queryID], index)
		new_query = reduction.reduce_byIDF_percentage(terms_idf, query_terms)
	elif ty == 'partial_Number':
		query_terms = query_lexicon(queries_narr[queryID], index)
		new_query = reduction.reduce_byIDF_number(terms_idf, query_terms)

	return query_lexicon(new_query, index)


def run_tests(s_lexicon, s_term_list, queries):
	"""This report runs processing of the queries comparing expansion and 
	reduction techniques. It runs against the VSM model."""

	indexes = ['single']
	types = ['control_title', 'control_desc', 'control_narr', 'RF_numDocs', 'RF_freqT', 'exp_Thesaurus', 'partial_Percent', 'partial_Number']
	data = {'control_title': {}, 'control_desc': {}, 'control_narr': {}, 'RF_numDocs': {}, 'RF_freqT': {}, 'exp_Thesaurus': {}, 'partial_Percent': {}, 'partial_Number': {}}
	measures = {'map', 'num_rel_ret', 'Rprec', 'P'}
	count = 1

	for index in indexes:
		if index == 'single':
			terms_by_doc, num_docs = build_document_index(s_lexicon)
			terms_idf = VSM_idf(s_term_list, num_docs)
		for ty in types:
			query_start = time.time()
			data = assign_description(ty, data)
			with open("results.txt", 'w') as resultsFile:
				for queryID in sorted(queries):
					score = {}
					query_terms = get_query(ty, queries, s_lexicon, s_term_list, queryID, score, index, terms_idf, terms_by_doc)
					score = send_to_SE('vsm', query_terms, s_lexicon, s_term_list, queryID, score, index)

					sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
					for idx, doc in enumerate(sorted_scores):
						if idx<100:
							resultsFile.write(queryID + ' ' + '0 ' + doc + ' ' + str(idx+1) + ' ' + str(sorted_scores[doc]) + ' ' + 'vsm' + '\n')
			query_end = time.time()
			data[ty][(index + '_QPT')]=str(query_end-query_start)

			for m in measures:
				status, output = commands.getstatusoutput(('./trec_eval -m  ' + m + ' qrel.txt results.txt'))
				if status == 0:
					output = output.replace('\t', ' ')
					if m == 'P':
						output = output.split('\nP_10')[0]
					result = output.split('all ')[1]
					data[ty][(index + '_' + m)] = result
				else:
					data[ty][(index + '_' + m)] = 'error'
			score.clear()
			print (str(count) + " out of 8 tests completed.")
			count += 1
	return data 


def send_to_SE(mdl, query_terms, s_lexicon, s_term_list, queryID, score, index):
	"""This report handles sending queries to the search engine depending on the index type."""

	score = Q_Score(mdl, query_terms, s_lexicon, s_term_list, queryID, score, index)
	return score






