import index
import os
import query_process
import output 
import time
import reduction

def rebuild_indexes():
	"""This function controls the building of the four
	indexes and prints statistics about the indexes."""

	in_path="BigSample/"

	input_files = []
	for filename in os.listdir(in_path):
		if filename != '.DS_Store':
			input_files.append(filename)

	memory_constraint = 0
	data = {}
	d_time = {}
	indexes = ['single', 'stem', 'positional', 'phrase']

	for indexType in indexes:
		data, d_time = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint, data, d_time)

	output.print_p1r1(data)


def read_single_stem():
	s_term_list, s_lexicon = index.read_in_file('single_terms', 'single_out_path', 'single')
	st_term_list, st_lexicon = index.read_in_file('stem_terms', 'stem_out_path', 'stem')

	return s_term_list, s_lexicon, st_term_list, st_lexicon


def query_options():
	opening = "\n\nPlease select a query processing option: \n"
	part2 = "   P - Report Processing for Project Part 2.\n"
	test = "   C - Compare SE peformance with query expansion and reduction.\n"
	quit = "   Q - Quit Search Engine."

	print (opening + part2 + test + quit)
	choice = raw_input()
	print "\n"

	return choice


def P_option(s_term_list, s_lexicon, st_term_list, st_lexicon):
	query_start = time.time()
	all_queries =  query_process.query_input("queryfile.txt")
	queries = {}
	for queryID in all_queries:
		queries[queryID] = all_queries[queryID]['title']

	data_r1 = query_process.report_1(s_lexicon, s_term_list, st_lexicon, st_term_list, queries, query_start)
	output.print_p2r1(data_r1)

	s_lexicon.clear()
	s_term_list.clear()

	p_term_list, p_lexicon = index.read_in_file('phrase_terms', 'phrase_out_path', 'phrase')
	po_term_list, po_lexicon = index.read_in_file('positional_terms', 'positional_out_path', 'positional')
	
	query_start = time.time()
	index_count, data_r2 = query_process.report_2(st_lexicon, st_term_list, p_lexicon, p_term_list, po_lexicon, po_term_list, queries, query_start)
	
	output.print_p2r2(data_r2, index_count)


def C_option (s_term_list, s_lexicon):

	all_queries = query_process.query_input("queryfile.txt")

	data = query_process.run_tests(s_lexicon, s_term_list, all_queries)
	output.print_p3(data)

