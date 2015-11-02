import preprocess
import math

def read_queries(query_file):
	"""This function reads the query file and 
	stores the query idea and query as a dictionary."""
	queryID='EMPTY'
	query=""
	queries={}

	with open(query_file, 'r') as queryFile:
		for line in queryFile:
			if "<num>" in line:
				queryID=line.replace('<num> Number: ', '')
				queryID=queryID.replace('\n','')
			elif queryID!='EMPTY':
				query=line.replace('<title> Topic:', '')
				query=query.replace('\n', '')
				queries[queryID]=query
				queryID='EMPTY'
				query=""
	return queries

def query_lexicon(query):
	terms = preprocess.processing(query, 'single')
	query_terms = {}

	for idx, term in enumerate(query_terms):
		if term in query_terms:
			query_terms[term] += 1
		else:
			query_terms[term] = 1
	print query_terms
	return query_terms


def build_document_index(index):
	"""This function builds diction of {docID: [terms in doc]}"""
	
	terms_by_document={}
	for term in index:
		for docID in term:
			if docID in terms_by_document:
				terms_by_document[docID].append(term)
			else:
				terms_by_document={docID:[term]}
	return terms_by_document


def VSM_Score(query, index, term_list, terms_by_doc, terms_idf):
	vsm_score = {}
	query_term_posting_list = []

	document_lengths = {}

	for term in query:
		query_term_weight=VSM()
		query_term_posting_list = index[term]
		for docID in query_term_posting_list:
			document_length, document_all_term_weights=VSM_document_length(terms_by_doc, terms_idf, index, docID)
			document_lengths[docID] = document_length
			if docID in vsm_score:
				vsm_score[docID] += document_all_term_weights[term] #* fh#weight of query term 
			else:
				vsm_score[docID] = document_all_term_weights[term] #* fh #weight of query term 

	for docID in vsm_score:
		vsm_score[docID] = vsm_score[docID] / sqrt(pow(document_length, 2))#*fj#length of the query)

	print hello

def VSM_document_length(terms_by_doc, term_idf, index, docID):
	"""This function build the document length for a specific document and
	returns the document length and the index of the term weights."""

	document_length = 0
	document_all_term_weights={}

	for term in terms_by_doc[docID]:
		term_weight = VSM_termWeight(docID,term_idf, term, index)
		document_all_term_weights[term] = term_weight
		document_length += pow(term_weight,2)

	for term in document_all_term_weights:
		document_all_term_weights[term] = document_all_term_weights[term] / document_length


	return document_length, document_all_term_weights


def VSM_termWeight(docID, term_idf, term, index):
	"""This function calculates the term weight for a term in a document."""

	weight = 0
	weight = (log(index[term][docID])+1)*term_idf[term]

	return weight


def VSM_idf(term_list):
	"""This function precalculates all the term idfs."""

	term_idf={}
	for term in term_list:
		term_idf[term]=log(term_list[term], 10)

	return term_idf




