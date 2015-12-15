from texttable import Texttable


def print_p1r1(data):
	"""This function prints the result of the building of the 
	indexes as required in Part 1. """

	indexes = ['single', 'stem', 'positional', 'phrase']

	t = Texttable()
	t.set_cols_width([10, 12, 8, 7, 7, 7, 7, 7])
	t.add_row(['Index', 'Construction', '-', '-', '-', '-', '-', '-'])
	t.add_row(['Index Type', 'Lexicon #', 'Index Size', 'Max df', 'Min df', 'Mean df', 'Median df', 'Time'])

	for idx in indexes: 
		t.add_row([idx, data[idx]['lexicon'], data[idx]['size'], data[idx]['max_df'], data[idx]['min_df'], data[idx]['mean_df'], data[idx]['median_df'], data[idx]['time']])

	print t.draw()


def merge_time_results(data, mem_constraint, indexType):
	"""This method prints the execution time results to the user.
	This method will only execute when there is a memory memory 
	constraint on the indexer."""

	indexes = ['single', 'stem', 'positional', 'phrase']

	t = Texttable()
	t.set_cols_width(15, 8)
	t.add_row(['-', '-', 'Triple list size'])
	t.add_row(['Statistics', 'Index Type', mem_constraint])
	t.add_row(['Time to create temp.', '-', '-'])
	for idx in indexes:
		t.add_row(['-', indexType, data[idx]['temp']])
	t.add_row(['Time to merge', '-', '-'])
	for idx in indexes:
		t.add_row(['-', indexType, data[idx]['merge']])
	t.add_row(['Total Build Time', '-', '-'])
	for idx in indexes:
		t.add_row(['-', indexType, data[idx]['total']])

	print t.draw()


def print_p2r1(data):
	"""This function prints the result of report 1 analysis
	from Project 2, Query Processing."""

	models = ['vsm', 'bm25', 'dirichlet']

	t = Texttable()
	t.add_row(['REPORT 1', '-', '-', '-', '-'])
	t.add_row(['-', 'SINGLE', '-', 'STEM', '-'])
	t.add_row(['Retrieval Model', 'MAP', 'Time', 'MAP', 'Time'])

	for mdl in models:
		t.add_row([mdl, data[mdl]['single_MAP'], data[mdl]['single_QPT'], data[mdl]['stem_MAP'], data[mdl]['stem_QPT']])
	print t.draw()


def print_p2r2(data, index_count):
	"""This report prints the result of Report 2 processing
	from Project 2, Query Processing."""

	print ('\n'+str(index_count['phrase']) + " queries processed against phrase index.")
	print (str(index_count['positional']) + " queries processed against positional index.")

	t = Texttable()
	t.add_row(['REPORT 2', '-', '-'])
	t.add_row(['Retrieval Model', 'MAP', 'Total Time'])
	t.add_row(['bm25', data['MAP'], data['QPT']])
	print t.draw()


def print_p3(data):
	"""This function prints the trec eval results for 
	project part 3 analysis."""

	#data = {type:{'single_map: #, single_num_rel_ret: #, single_P: #, single_RPrec: #, single_QPT: #, desc: text'}}
	types = ['control_title', 'control_desc', 'control_narr', 'RF_numDocs', 'RF_freqT', 'exp_Thesaurus', 'partial_Percent', 'partial_Number']

	print '\n\n\n'

	t = Texttable()
	t.set_cols_width([15, 9, 9, 9, 9, 9, 50])
	t.add_row(['REPORT 3', 'VSM Model', '-', '-', '-', '-', '-'])
	t.add_row(['SINGLE Index', '-', '-', '-', '-', '-', '-'])
	t.add_row(['Type', 'MAP', 'Rel. Ret.', 'P@5', 'RPrec', 'Time', 'Description'])
	
	for ty in types:
		t.add_row([ty, data[ty]['single_map'], data[ty]['single_num_rel_ret'], data[ty]['single_P'], data[ty]['single_Rprec'], data[ty]['single_QPT'], data[ty]['explanation']])
	print t.draw()








