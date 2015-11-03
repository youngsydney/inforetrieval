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



"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR VSM COSINE"""



def VSM_idf(term_list, num_docs):
	"""This function precalculates all the term idfs."""

	terms_idf={}
	for term in term_list:
		terms_idf[term]=math.log10((float(num_docs)/term_list[term]))

	return terms_idf


def VSM_Score(query_terms, index, term_list, terms_by_doc, terms_idf):
	#will be a dictionary of {docID:score, docID:score}
	vsm_score = {}
	dict_term_weights = {}

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
			print term

	for docID in vsm_score:
		vsm_score[docID] = vsm_score[docID] / math.sqrt(pow(VSM_sum_termWeights_doc(dict_term_weights, docID),2)*pow(VSM_sum_termWeights_query(query_termWeights), 2))

	return vsm_score



def VSM_termWeight_numerator(term_idf, termFreq):
	"""This function calculates the term weight for a term in a document."""
	weight = 0
	weight = (math.log(termFreq)+1)*term_idf

	return weight

def VSM_termWeight(docID, terms_idf, index, terms_in_docID, dict_term_weights):
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
	sum_weights=0
	for term in dict_term_weights[docID]:
		sum_weights += dict_term_weights[docID][term]

	return sum_weights

def VSM_sum_termWeights_query(query_termWeights):
	
	sum_weights=0
	for term in query_termWeights:
		sum_weights += query_termWeights[term]

	return sum_weights

def VSM_query_termWeight(terms_idf, index, query_terms):
	
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

def BM25_Score(query_terms, index, term_list):

	bm25_score = {}
	k1 = 1.2
	k2 = 1000
	b = 0.75

	document_lengths, average_length, num_docs = build_BM25_document_lengths(index)

	for term in query_terms:
		if term in index:
			term_weight = BM25_weight(term_list, term, num_docs)
			B = ((k2 + 1) * query_terms[term]) / (k2 + query_terms[term])
			query_term_posting_list = index[term]

			for docID in query_term_posting_list:
				A = ((k1 + 1) * index[term][docID]) / (index[term][docID] + k1 * (1 - b + b * (document_lengths[docID] / average_length)))
				if docID not in bm25_score:
					bm25_score[docID] = term_weight * A * B 
				else:
					bm25_score[docID] += term_weight * A * B 
		else:
			print term

	return bm25_score

