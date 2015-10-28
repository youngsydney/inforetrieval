import preprocess
import index
import heapq
import time
import os

in_path="BigSample/"


if __name__ == "__main__":
	"""This is the main method 
	which drives the control"""

	start_time = time.time()
	
	indexes = ['single', 'stem', 'phrase', 'positional']
	input_files = []

	for filename in os.listdir(in_path):
		if filename != '.DS_Store':
			input_files.append(filename)

	for indexType in indexes:
		index.iterate_through_folder(in_path, input_files, (indexType + "_out_path"), (indexType + "_terms"), indexType)

	end_time = time.time()

	print ("\nTotal Time of Execution for Index Construction: " + str(end_time - start_time) + '\n')

	#Here read in the query file and begin the query processing 

