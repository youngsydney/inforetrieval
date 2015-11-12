import preprocess
import math


def query_input(query_file):
	queryID = 'EMPTY'
	title = ''
	desc = ''
	narr = ''
	nextLine = ''
	add = ''
	queries = {}

	with open(query_file, 'r') as queryFile:
		for line in queryFile:
			if queryID == 'EMPTY' and "<num>" in line:
				queryID=line.replace('<num> Number: ', '')
				queryID=queryID.replace('\n','')
			elif title == '' and "<title>" in line:
				title=line.replace('<title> Topic:', '')
				title=title.replace('\n', '')
			elif desc == '' and nextLine == '':
				nextLine = 'desc'
			elif nextLine == 'desc':
				if "<narr>" in line:
					nextLine = 'narr'
				else:
					add = line.replace('<desc> Description:', '')
					add = add.replace('\n',' ')
					desc += add
					add = ''
			elif nextLine == 'narr':
				if "<top>" in line:
					queries[queryID] = {"title":title, "desc":desc, "narr":narr}
					queryID = 'EMPTY'
					title = ''
					desc = ''
					narr = ''
					nextLine = ''
				else:
					add = line.replace('\n',' ')
					add = add.replace('</top>', ' ')
					narr += add
					add = ''
	return queries


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

def query_lexicon(query, index_type):
	terms = preprocess.processing(query, index_type)
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



def VSM_idf(term_list, num_docs):
	"""This function precalculates all the term idfs."""

	terms_idf={}
	for term in term_list:
		terms_idf[term]=math.log10((float(num_docs)/term_list[term]))

	return terms_idf


def VSM_Score(query_terms, index, term_list):
	#will be a dictionary of {docID:score, docID:score}
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
			#print term

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

def BM25_Score(query_terms, index, term_list, queryID, score, indexType):

	if indexType == 'positional':
		score = BM25_Score_Positional(query_terms, index, term_list, queryID, score)
		return score
	k1 = 1.2
	k2 = 1000
	#check query by query to update the constants, should change on a query by query basis?????
	b = 0.75

	document_lengths, average_length, num_docs = build_BM25_document_lengths(index)
	for term in query_terms:
		if term in index:
			term_weight = BM25_weight(term_list, term, num_docs)
			B = ((k2 + 1) * query_terms[term]) / (k2 + query_terms[term])
			query_term_posting_list = index[term]

			for docID in query_term_posting_list:
				A = ((k1 + 1) * len(index[term][docID])) / (len(index[term][docID]) + k1 * (1 - b + b * (document_lengths[docID] / average_length)))
				if docID not in score:
					score[docID] = term_weight * A * B 
				else:
					score[docID] += term_weight * A * B 
		else:
			#print term
			#print queryID
			pass

	return score

def BM25_Score_Positional(query_terms, index, term_list, queryID, score):
	"""ASK PROFESSOR"""
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
				if docID not in score:
					score[docID] = term_weight * A * B 
				else:
					score[docID] += term_weight * A * B 
		else:
			#print term
			#print queryID
			pass

	
	return score


"""THIS IS THE SECTION WHICH HANDLES QUERY PROCESSING FOR Dirichlet Smoothing"""

def Dirichlet_Score(query_terms, index):

	dirichlet_score = {}
	doc_numerator_value = 0 
	doc_denominator_value = 0
	average_length = 0
	# |C| num terms in the entire collection 

	document_lengths, average_length, collection_length = build_Dirichlet_doc_collection_length(index)
	tf_collection = build_tf_in_collection(index)

	for term in query_terms:
		if term in index: 
			query_term_posting_list = index[term]
			for docID in query_term_posting_list:

				numerator = index[term][docID] + (average_length + (float(tf_collection[term]) / collection_length))
				denominator = document_lengths[docID] + average_length

				if docID not in dirichlet_score:
					dirichlet_score[docID] = math.log((float(numerator) / denominator))
				else:
					dirichlet_score[docID] += math.log((float(numerator) / denominator))
		else:
			#print term
			pass

	return dirichlet_score


def build_Dirichlet_doc_collection_length(index):
	
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
	tf_collection = {}

	for term in index:
		for docID in index[term]:
			if term in tf_collection:
				tf_collection[term] += index[term][docID]
			else:
				tf_collection[term] = index[term][docID]

	return tf_collection











