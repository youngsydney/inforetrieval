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


	"""THIS IS THE SECTION WHICH CONSTRUCTS THE INDEX."""
	start_time = time.time()
	
	#indexes = ['single', 'stem', 'phrase', 'positional']
	indexes = ['single', 'stem']
	input_files = []

	for filename in os.listdir(in_path):
		if filename != '.DS_Store':
			input_files.append(filename)

	#set the memory constrant to 1000, 10000, or 100000 -- a memory constraint of 0 means no memory constraint
	memory_constraint = 0

	for indexType in indexes:
		if indexType == 'single':
			s_term_list, s_lexicon = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint)
		elif indexType == 'stem':
			st_term_list, st_lexicon = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint)

	end_time = time.time()

	print ("\nTotal Time of Execution for Index Construction: " + str(end_time - start_time) + '\n')




	"""THIS IS THE SECTION WHICH PROCESSES THE QUERIES."""

	queries = query_process.read_queries("queryfile.txt")
	
	types = {'vsm', 'bm25', 'dirichlet'}
	data = {'vsm':{'S_MAP':'', 'S_QPT': '', 'ST_MAP': '', 'ST_QPT': ''}, 'bm25':{'MAP':'', 'QPT': '', 'ST_MAP': '', 'ST_QPT': ''}, 'dirichlet':{'MAP':'', 'QPT': '', 'ST_MAP': '', 'ST_QPT': ''}}
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
						score = query_process.BM25_Score(query_terms, s_lexicon, s_term_list, queryID)
					elif processing_type == 'bm25' and index_type == 'stem':
						score = query_process.BM25_Score(query_terms, st_lexicon, st_term_list, queryID)
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
				data[processing_type]['S_QPT'] = str(query_end-query_start)
			elif indexType == 'stem':
				data[processing_type]['ST_QPT'] = str(query_end-query_start)
			status, output = commands.getstatusoutput("./trec_eval -m map ~/Documents/searchengine/qrel.txt ~/Documents/searchengine/results.txt")
			output = output.replace ('\t', ' ')
			MAP_number = output.split('all ')[1]
			if index_type == 'single':
				data[processing_type]['S_MAP'] = MAP_number
			elif index_type == 'stem':
				data[processing_type]['ST_MAP'] = MAP_number
		
	t = Texttable()
	t.add_row(['-', 'SINGLE', '-', 'STEM', '-'])
	t.add_row(['Query Processor', 'MAP', 'Time', 'MAP', 'Time'])
	t.add_row(['vsm', data['vsm']['S_MAP'], data['vsm']['S_QPT'], data['vsm']['ST_MAP'], data['vsm']['ST_QPT']])
	t.add_row(['bm25', data['bm25']['S_MAP'], data['bm25']['S_QPT'], data['bm25']['ST_MAP'], data['bm25']['ST_QPT']])
	t.add_row(['dirichlet', data['dirichlet']['S_MAP'], data['dirichlet']['S_QPT'], data['dirichlet']['ST_MAP'], data['dirichlet']['ST_QPT']])
	print t.draw()




