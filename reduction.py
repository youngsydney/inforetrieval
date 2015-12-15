from collections import OrderedDict
from operator import itemgetter
import query_process
import time
import math
import commands
from PyDictionary import PyDictionary


def reduce_byIDF_percentage(terms_idf, query_terms):
	"""This function selects the terms within a query to 
	process based on their idf times their tf in the query. 
	It choses the top ___ percentage."""

	percentage = 72
	M = len(query_terms) * percentage / 100
	query_idf = {}

	for term in query_terms: 
		if term in terms_idf:
			query_idf[term] = terms_idf[term] * query_terms[term]
	sorted_query = OrderedDict(sorted(query_idf.items(), key=itemgetter(1), reverse=True))

	new_query = ' '
	for idx, term in enumerate(sorted_query):
		if idx < M:
			new_query += (term + ' ')

	return new_query


def reduce_byIDF_number(terms_idf, query_terms):
	"""This function selects the terms within a query to process based
	on their idf times ther tf in the query. It choses from the top _____ number."""

	M = 16
	query_idf = {}

	for term in query_terms: 
		if term in terms_idf:
			query_idf[term] = terms_idf[term] * query_terms[term]
	sorted_query = OrderedDict(sorted(query_idf.items(), key=itemgetter(1), reverse=True))

	new_query = ' '

	for idx, term in enumerate(sorted_query):
		if idx < M:
			new_query += (term + ' ')

	return new_query