import preprocess
import tempfile
import os
import heapq
import time
import statistics

memory_constraint=0
term_dict={}
lexicon={}
count=0


def iterate_through_folder(folderPath, input_files, out_path, out_terms, indexType, memory):
	"""This method iterates through the files in the folder, sends them
	to the document iterator, and then handles the final temp writing and merging."""

	start_time = time.time()
	merge_time=0

	global memory_constraint
	memory_constraint=memory

	temp_files = []

	for filename in input_files:
		temp_files = iterate_through_files(temp_files, folderPath, filename, indexType)

	if not temp_files and memory_constraint != 0:
		if indexType == 'positional':
			write_to_file_position(out_path)
		else:
			write_to_file(out_path)
		merge_time = 0
	elif temp_files and memory_constraint != 0:
		if indexType == 'positional':
			temp_files = write_to_temp_position(temp_files)
		else:
			temp_files = write_to_temp(temp_files)
		merge_time = time.time()
		merge_temps(temp_files, out_path)

	end_time=time.time()

	numT, maxT,minT,meanT, medianT = calculate_term_list()

	time_results(start_time, merge_time, end_time, numT, maxT,minT,meanT, medianT, indexType)

	if memory_constraint == 0:
		return term_dict, lexicon
	else:
		write_term_list(out_terms)


def iterate_through_files(temp_files, folder, singleFile, indexType):
	"""This method reads in a file and stores each document as an item in a list (collection). 
	Then it sends each document within the collection to be added to the index."""


	doc_collection = preprocess.read_collection(folder+singleFile)
	for document in doc_collection:
		docID = preprocess.get_docID(document)
		if indexType == 'single':
			temp_files = build_single_index(temp_files, document, docID)
		elif indexType == 'phrase':
			temp_files = build_phrase_index(temp_files, document, docID)
		elif indexType == 'stem':
			temp_files = build_stem_index(temp_files, document, docID)
		elif indexType == 'positional':
			temp_files = build_positional_index(temp_files, document, docID)
	return temp_files


def build_single_index(temp_files, document, docID):
	"""This method controls the processing of a document and the adding of the terms
	to the single index."""
	terms = preprocess.processing(document, 'single')
	append_to_index(terms, docID)
	temp_files = check_mem_constraint(temp_files)
	return temp_files


def build_stem_index(temp_files, document, docID):
	"""This method controls the processing of a document and the adding 
	of the terms to the stem index."""

	stems = preprocess.processing(document, 'stem')
	append_to_index(stems, docID)
	temp_files = check_mem_constraint(temp_files)
	return temp_files


def build_phrase_index(temp_files, document, docID):
	"""This method controls the processing of a document and the adding
	of the terms to the phrase index."""

	phrases = preprocess.processing(document, 'phrase')
	append_to_index(phrases, docID)
	temp_files = check_mem_constraint(temp_files)
	return temp_files


def build_positional_index(temp_files, document, docID):
	"""This method controls the processing of a document and the adding
	of the terms to the phrase index."""

	tokens = preprocess.processing(document, 'positional')
	append_to_index_position(tokens, docID)
	
	global count
	global memory_constraint

	if count > memory_constraint and memory_constraint != 0:
		temp_files = write_to_temp_position(temp_files)
		count = 0
	return temp_files

def check_mem_constraint(temp_files):
	"""This method checks if the memory has reached the constraint, if it has
	then the method calls write_to_temp to write to disk memory."""

	global count
	global memory_constraint

	if count > memory_constraint and memory_constraint != 0:
		temp_files = write_to_temp(temp_files)
		count = 0
	return temp_files


def append_to_index(terms, docID):
	""""This method iterates through the terms and sends each
	key to be added to the index."""

	global count
	for term in terms:
		add_to_index(term, docID)
		count += 1

def append_to_index_position(terms, docID):
	""""This method iterates through the terms and sends each
	key to be added to the POSITIONAL index."""
	
	global lexicon 
	global term_dict
	global count
	for idx, token in enumerate(terms):
		add_to_index_position(token, idx, docID)
		count += 1

def add_to_index(term, docID):
	"""This method checks if the term is already in the term list
	and if the docID is already in the posting list of that term. 
	Then it either updates the df, the tf, and/or adds new document.
	Increments the count when a new document added to the posting list."""
	
	global lexicon 
	global count
	global term_dict
	if term in lexicon and docID in lexicon[term]:
		#Second+ time term seen in document, add one to tf
		lexicon[term][docID] += 1
	elif term in lexicon and docID not in lexicon[term]:
		#term seen in another document, add to posting list and update df
		lexicon[term][docID] = 1
		term_dict[term] += 1
	elif term not in lexicon and term in term_dict:
		#add term to lexicon and update df
		lexicon[term] = {docID:1}
		term_dict[term] += 1
	elif term not in lexicon and term not in term_dict:
		#add term to lexicon and to the term list
		lexicon[term] = {docID:1}
		term_dict[term] = 1


def add_to_index_position(term, position, docID):
	"""This method does the same as add_to_index except for the
	POSITIONAL index. In the posting list instead of storing tf, the 
	document maps to a list of the positions. The tf could be found
	by finding the length of the list. """

	global lexicon 
	global count
	global term_dict
	if term in lexicon and docID in lexicon[term]:
		lexicon[term][docID].append(position)
	elif term in lexicon and docID not in lexicon[term]:
		lexicon[term][docID] = [position]
		term_dict[term] += 1
	elif term not in lexicon and term in term_dict:
		lexicon[term] = {docID:[position]}
		term_dict[term] += 1
	elif term not in lexicon and term not in term_dict:
		lexicon[term] = {docID:[position]}
		term_dict[term] = 1


def write_to_temp(temp_files):
	"""This file writes the lexicon to a temp file and stores
	the name of the temp file in a list. It then deletes the 
	contents of the lexicon."""

	global lexicon 
	global count
	os_temp,temp_file_name = tempfile.mkstemp()
	for term in sorted(lexicon.keys()):
		os.write(os_temp,'<' + term + '> ')
		for docID in lexicon[term]:
			os.write(os_temp, docID + ',' + str(lexicon[term][docID]) + ' | ')
		os.write(os_temp,'\n')
	lexicon = {}
	count = 0
	if temp_files:
		temp_files.append(str(temp_file_name))
	else:
		temp_files = [str(temp_file_name)]
	os.close(os_temp)
	return temp_files


def write_to_temp_position(temp_files):
	"""This file writes the POSITIONAL lexicon to a temp file and stores
	the name of the temp file in a list. It then deletes the 
	contents of the lexicon."""

	global lexicon 
	global count
	os_temp,temp_file_name = tempfile.mkstemp()
	for term in sorted(lexicon.keys()):
		os.write(os_temp,'<' + term + '> ')
		for docID in lexicon[term]:
			os.write(os_temp,docID)
			os.write(os_temp, str(lexicon[term][docID]))
			os.write(os_temp, ' | ')
		os.write(os_temp, '\n')
	lexicon = {}
	count = 0
	if temp_files:
		temp_files.append(str(temp_file_name))
	else:
		temp_files = [str(temp_file_name)]
	os.close(os_temp)
	return temp_files


def write_to_file(out_file):
	"""This method handles the case in which no temp files 
	were created and the entire lexicon/pl is stored in memory
	and now is written to the final file."""

	global lexicon 
	global count
	with open(out_file, 'w') as outFile:
		for term in sorted(lexicon.keys()):
			outFile.write('<' + term + '> ')
			for docID in lexicon[term]:
				outFile.write(docID + ',' + str(lexicon[term][docID]) + ' | ')
			outFile.write('\n')
		lexicon = {}
		count = 0


def write_to_file_position(out_file):
	"""This method handles the case in which no temp files 
	were created and the entire lexicon/pl is stored in memory
	and now is written to the final file for POSITIONAL."""
	
	global lexicon 
	global count
	with open(out_file, 'w') as outFile:
		for term in sorted(lexicon.keys()):
			outFile.write('<' + term + '> ')
			for docID in lexicon[term]:
				outFile.write(docID + ' ')
				outFile.write(str(lexicon[term][docID]))
				outFile.write(' | ')
			outFile.write('\n')
		lexicon = {}
		count = 0


def calculate_term_list():
	num_of_terms = len(term_dict)
	max_df = max(term_dict.values())
	min_df = min(term_dict.values())
	mean_df = statistics.mean(term_dict.values())
	median_df = statistics.median(term_dict.values())

	return num_of_terms, max_df, min_df, mean_df, median_df

def write_term_list(out_file):
	"""This method writes the term list containing all the 
	terms and the document frequency to the final file. """

	global term_dict
	with open(out_file, 'w') as outFile:
		for term in sorted(term_dict):
			outFile.write('<' + term + '> ' + str(term_dict[term]) + '\n')
		term_dict = {}


def decorated_file(t_file, key):
	"""Helpder for merge."""

	for line in t_file:
		key_and_doc = key(line)
		yield (key_and_doc[0], key_and_doc[1])

def key_func(line):
	"""Helper for merge."""
	line = line.replace('\n', '')
	return line.split('>', 2)


def grouper(sequence, size):
	"""Taken from http://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
	Returns a list broken in to items as specified by size. Using in this program to step by step merge."""
	return (sequence[pos:pos + size] for pos in xrange(0, len(sequence), size))


def merge_temps(temp_files, out_path, keyfunc=key_func):
	"""This method opens all the temp files and merges them together,
	adding them to the final file that contains the entire lexicon. 
	NOTE: TAKEN FROM: http://stackoverflow.com/questions/1001569/python-class-to-merge-sorted-files-how-can-this-be-improved
	and uses the merge from heapq."""

	incrementalMergeFiles = []

	if len(temp_files)>200:
		#First merge in groups of 50 into temp files
		for group in grouper(temp_files, 50):
			current_term = ''
			combined_posting_list = ''
			files = map(open, group)
			os_temp, temp_file_name = tempfile.mkstemp()
			for line in heapq.merge(*[decorated_file(f, keyfunc) for f in files]):
				if current_term == '':
					current_term = line[0]
					combined_posting_list = line[1]
				elif line[0] == current_term:
					combined_posting_list += line[1]
				elif line[0] != current_term:
					os.write(os_temp, (current_term + '>' + combined_posting_list + '\n'))
					current_term = line[0]
					combined_posting_list = line[1]
			for openfile in files:
				openfile.close()
			incrementalMergeFiles.append(temp_file_name)
			os.close(os_temp)
	else:
		incrementalMergeFiles = temp_files

	files = map(open, incrementalMergeFiles)
	current_term = ''
	combined_posting_list = ''
	
	with open(out_path, 'w') as outfile:
		#now merge the files into the file path
		for line in heapq.merge(*[decorated_file(f, keyfunc) for f in files]):
			if current_term == '':
				current_term = line[0]
				combined_posting_list = line[1]
			elif line[0] == current_term:
				combined_posting_list += line[1]
			elif line[0] != current_term:
				outfile.write(current_term + '>' + combined_posting_list + '\n')
				current_term = line[0]
				combined_posting_list = line[1]

	for openfile in files:
		openfile.close()
	for temp in temp_files:
		os.remove(temp)
	del temp_files


def time_results(start_time, merge_time, end_time, numT, maxT,minT,meanT, medianT, indexType):
	"""This method prints the execution time results to the user."""

	if indexType == 'single':
		print ("\nSINGLE INDEX")
	elif indexType == 'stem':
		print ("\nSTEM INDEX")
	elif indexType == 'phrase':
		print ("\nPHRASE INDEX")
	elif indexType == 'positional':
		print ("\nPOSITIONAL INDEX")

	print ("Execution Time Total: " + str(end_time - start_time))
	if merge_time != 0:
		print ("Time to Temp File Creation: " + str(merge_time - start_time))
		print ("Time to Merge Temp Files: " + str(end_time - merge_time))

	print ("Terms in lexicon: " + str(numT))
	print ("Max df: " + str(maxT))
	print ("Min df: " + str(minT))
	print ("Mean df: " + str(meanT))
	print ("Median df: " + str(medianT))
