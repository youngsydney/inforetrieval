import preprocess
import index
import heapq
import time
import os
import query_process
from collections import OrderedDict
from operator import itemgetter
from texttable import Texttable
#import os
import commands

in_path="BigSample/"


if __name__ == "__main__":
	"""This is the main method 
	which drives the control"""

	print "Please expect approximately 2 minutes to construct the indexes and an additional 30 seconds to do query processing analysis. "

	"""THIS IS THE SECTION WHICH CONSTRUCTS THE INDEX."""
	start_time = time.time()

	indexes = ['single', 'stem', 'phrase', 'positional']
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

	end_time = time.time()
	print ("\nTotal Time of Execution for Index Construction: " + str(end_time - start_time))

	t_p1r1 = Texttable()
	t_p1r1.add_row(['Index', 'Construction', '-', '-', '-', '-', '-', '-'])
	t_p1r1.add_row(['Index Type', 'Lexicon #', 'Index Size', 'Max df', 'Min df', 'Mean df', 'Median df', 'Time'])
	t_p1r1.add_row(['single', data_p1r1['single']['lexicon'], data_p1r1['single']['size'], data_p1r1['single']['max_df'], data_p1r1['single']['min_df'], data_p1r1['single']['mean_df'], data_p1r1['single']['median_df'], data_p1r1['single']['time']])
	t_p1r1.add_row(['stem', data_p1r1['stem']['lexicon'], data_p1r1['stem']['size'], data_p1r1['stem']['max_df'], data_p1r1['stem']['min_df'], data_p1r1['stem']['mean_df'], data_p1r1['stem']['median_df'], data_p1r1['stem']['time']])
	t_p1r1.add_row(['phrase', data_p1r1['phrase']['lexicon'], data_p1r1['phrase']['size'], data_p1r1['phrase']['max_df'], data_p1r1['phrase']['min_df'], data_p1r1['phrase']['mean_df'], data_p1r1['phrase']['median_df'], data_p1r1['phrase']['time']])
	t_p1r1.add_row(['positional', data_p1r1['positional']['lexicon'], data_p1r1['positional']['size'], data_p1r1['positional']['max_df'], data_p1r1['positional']['min_df'], data_p1r1['positional']['mean_df'], data_p1r1['positional']['median_df'], data_p1r1['positional']['time']])
	print t_p1r1.draw()



	"""THIS IS THE SECTION WHICH PROCESSES THE QUERIES."""

	print ('\nQuery Processing')

	queries = query_process.read_queries("queryfile.txt")
	types = {'vsm', 'bm25', 'dirichlet'}
	data_r1 = {'vsm':{'S_MAP':'', 'S_QPT': '', 'ST_MAP': '', 'ST_QPT': ''}, 'bm25':{'MAP':'', 'QPT': '', 'ST_MAP': '', 'ST_QPT': ''}, 'dirichlet':{'MAP':'', 'QPT': '', 'ST_MAP': '', 'ST_QPT': ''}}
	report1_indexes = ['single', 'stem']

	for index_type in report1_indexes:
		for processing_type in types:
			query_start = time.time()
			with open("results.txt", 'w') as resultsFile:
				for queryID in sorted(queries):
					score = {}
					query_terms = query_process.query_lexicon(queries[queryID], index_type)
					if processing_type == 'vsm' and index_type == 'single':
						score = query_process.VSM_Score(query_terms, s_lexicon, s_term_list)
					elif processing_type == 'vsm' and index_type == 'stem':
						score = query_process.VSM_Score(query_terms, st_lexicon, st_term_list)
					elif processing_type == 'bm25' and index_type == 'single':
						score = query_process.BM25_Score(query_terms, s_lexicon, s_term_list, queryID, score, 'single')
					elif processing_type == 'bm25' and index_type == 'stem':
						score = query_process.BM25_Score(query_terms, st_lexicon, st_term_list, queryID, score, 'stem')
					elif processing_type == 'dirichlet' and indexType == 'single':
						score = query_process.Dirichlet_Score(query_terms, s_lexicon)
					elif processing_type == 'dirichlet' and indexType == 'stem':
						score = query_process.Dirichlet_Score(query_terms, st_lexicon)
					sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
					for idx, doc in enumerate(sorted_scores):
						if idx<100:
							resultsFile.write(queryID + ' ' + '0 ' + doc + ' ' + str(idx+1) + ' ' + str(sorted_scores[doc]) + ' ' + processing_type + '\n')
			query_end = time.time()
			if index_type == 'single':
				data_r1[processing_type]['S_QPT'] = str(query_end-query_start)
			elif indexType == 'stem':
				data_r1[processing_type]['ST_QPT'] = str(query_end-query_start)
			status, output = commands.getstatusoutput("./trec_eval -m map ~/Documents/searchengine/qrel.txt ~/Documents/searchengine/results.txt")
			if status == 0:
				output = output.replace ('\t', ' ')
				MAP_number = output.split('all ')[1]
				if index_type == 'single':
					data_r1[processing_type]['S_MAP'] = MAP_number
				elif index_type == 'stem':
					data_r1[processing_type]['ST_MAP'] = MAP_number
			else:
				if index_type == 'single':
					data_r1[processing_type]['S_MAP'] = "error"
				elif index_type == 'stem':
					data_r1[processing_type]['ST_MAP'] = "error"
		
	t_p2r1 = Texttable()
	t_p2r1.add_row(['REPORT 1', '-', '-', '-', '-'])
	t_p2r1.add_row(['-', 'SINGLE', '-', 'STEM', '-'])
	t_p2r1.add_row(['Retrieval Model', 'MAP', 'Time', 'MAP', 'Time'])
	t_p2r1.add_row(['vsm', data_r1['vsm']['S_MAP'], data_r1['vsm']['S_QPT'], data_r1['vsm']['ST_MAP'], data_r1['vsm']['ST_QPT']])
	t_p2r1.add_row(['bm25', data_r1['bm25']['S_MAP'], data_r1['bm25']['S_QPT'], data_r1['bm25']['ST_MAP'], data_r1['bm25']['ST_QPT']])
	t_p2r1.add_row(['dirichlet', data_r1['dirichlet']['S_MAP'], data_r1['dirichlet']['S_QPT'], data_r1['dirichlet']['ST_MAP'], data_r1['dirichlet']['ST_QPT']])
	print t_p2r1.draw()


	data_r2 = {'bm25':{'P_MAP':'', 'P_QPT': ''}}
	index_count = {'phrase': 0, 'positional': 0}

	query_start = time.time()
	with open("results.txt", 'w') as resultsFile:
		for queryID in sorted(queries):
			index_decision = query_process.makeDecision(query_terms, p_term_list)
			index_count[index_decision] += 1

			query_terms = query_process.query_lexicon(queries[queryID], index_decision)

			score = {}
			if index_decision == 'phrase':
				score = query_process.BM25_Score(query_terms, p_lexicon, p_term_list, queryID, score, 'phrase')
			elif index_decision == 'positonal':
				score = query_process.BM25_Score(query_terms, po_lexicon, po_term_list, queryID, score, 'positional')
			if len(score) < 99:
				query_terms = query_process.query_lexicon(queries[queryID], 'stem')
				score = query_process.BM25_Score(query_terms, st_lexicon, st_term_list, queryID, score, 'stem')
			sorted_scores = OrderedDict(sorted(score.items(), key=itemgetter(1), reverse=True))
			for idx, doc in enumerate(sorted_scores):
				if idx<100:
					resultsFile.write(queryID + ' ' + '0 ' + doc + ' ' + str(idx+1) + ' ' + str(sorted_scores[doc]) + ' ' + 'phrase_stem '  + '\n')
	query_end = time.time()
	data_r2['bm25']['P_QPT'] = str(query_end-query_start)
	status, output = commands.getstatusoutput("./trec_eval -m map ~/Documents/searchengine/qrel.txt ~/Documents/searchengine/results.txt")
	output = output.replace ('\t', ' ')
	MAP_number = output.split('all ')[1]
	data_r2['bm25']['P_MAP'] = MAP_number

	print ('\n'+str(index_count['phrase']) + " queries processed against phrase index.")
	print (str(index_count['positional']) + " queries processed against positional index.")
	t_p2r2 = Texttable()
	t_p2r2.add_row(['REPORT 2', '-', '-'])
	t_p2r2.add_row(['Retrieval Model', 'MAP', 'Time'])
	t_p2r2.add_row(['bm25', data_r2['bm25']['P_MAP'], data_r2['bm25']['P_QPT']])
	print t_p2r2.draw()

