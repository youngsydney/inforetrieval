import preprocess
import index
import heapq
import time
import os
import query_process
from collections import OrderedDict
from operator import itemgetter

in_path="BigSample/"


if __name__ == "__main__":
	"""This is the main method 
	which drives the control"""

	start_time = time.time()
	
	#indexes = ['single', 'stem', 'phrase', 'positional']
	indexes = ['single']
	input_files = []

	for filename in os.listdir(in_path):
		if filename != '.DS_Store':
			input_files.append(filename)

	#set the memory constrant to 1000, 10000, or 100000 -- a memory constraint of 0 means no memory constraint
	memory_constraint = 0

	for indexType in indexes:
		term_list, lexicon = index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType, memory_constraint)

	end_time = time.time()

	print ("\nTotal Time of Execution for Index Construction: " + str(end_time - start_time) + '\n')

	#Here read in the query file and begin the query processing 
	terms_by_doc = query_process.build_document_index(lexicon)
	terms_idf = query_process.VSM_idf(term_list)

	queries = query_process.read_queries("queryfile.txt")

	with open("results.txt", 'w') as resultsFile:
		for queryID in sorted(queries):
			vsm_score={}
			query_terms = query_process.query_lexicon(queries[queryID])

			vsm_score = query_process.VSM_Score(query_terms, lexicon, term_list, terms_by_doc, terms_idf)
			sorted_scores = OrderedDict(sorted(vsm_score.items(), key=itemgetter(1), reverse=True))
			for idx, doc in enumerate(sorted_scores):
				if idx<100:
					resultsFile.write(queryID + ' ' + '0 ' + doc + ' ' + str(idx) + ' ' + str(sorted_scores[doc]) + ' ' + 'COSINE\n')





