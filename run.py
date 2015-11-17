import preprocess
import index
import heapq
import time
import os
import query_process


in_path="BigSample/"


if __name__ == "__main__":
	"""This is the main method 
	which drives the control"""

	print "Please expect approximately 2.5 minutes for the program to run. "


	"""THIS IS THE SECTION WHICH CONSTRUCTS THE INDEX."""


	indexes = ['single', 'stem']

	input_files = []
	for filename in os.listdir(in_path):
		if filename != '.DS_Store':
			input_files.append(filename)

	#set the memory constrant to 1000, 10000, or 100000 -- a memory constraint of 0 means no memory constraint
	memory_constraint = 0
	data_p1r1 = {}

	for indexType in indexes:
		if indexType == 'single':
			s_term_list, s_lexicon, data_p1r1 = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data_p1r1)
		elif indexType == 'stem':
			st_term_list, st_lexicon, data_p1r1 = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data_p1r1)
		elif indexType == 'phrase':
			p_term_list, p_lexicon, data_p1r1 = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data_p1r1)
		elif indexType == 'positional':
			po_term_list, po_lexicon, data_p1r1 = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data_p1r1)

	index.print_results(data_p1r1)


	"""THIS IS THE SECTION WHICH PROCESSES THE QUERIES."""

	print ('\nQuery Processing')
	query_start = time.time()
	all_queries =  query_process.query_input("queryfile.txt")
	queries = {}
	for queryID in all_queries:
		queries[queryID] = all_queries[queryID]['title']

	data_r1 = query_process.report_1(s_lexicon, s_term_list, st_lexicon, st_term_list, queries, query_start)
	query_process.print_results1(data_r1)
"""
	#have to clear the single index for memory reasons
	s_lexicon.clear()
	s_term_list.clear()

	indexes = ['phrase', 'positional']
	for indexType in indexes:
		if indexType == 'phrase':
			p_term_list, p_lexicon, data_p1r1 = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data_p1r1)
		elif indexType == 'positional':
			po_term_list, po_lexicon, data_p1r1 = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data_p1r1)

	query_start = time.time()
	index_count, data_r2 = query_process.report_2(st_lexicon, st_term_list, p_lexicon, p_term_list, po_lexicon, po_term_list, queries, query_start)
	query_process.print_results2(data_r2, index_count)
"""
