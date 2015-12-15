READ_ME

Sydney Young
December 14, 2015
COSC 488: Introduction to Information Retrieval

How to Run: 
	On the command line -- navigate to the project directory and type "python run.py" to compile and run the run.py file.

	The program will provide the user with multiple options. 

	First, the program will ask the user if there would like to rebuild the indexes. Enter Y to rebuild all four indexes,
	enter N to read in the indexes from memory.

	Second, the program will ask the user what type of query processing they would like to perform. Enter P for Project 2
	reporting and a comparison of BM25, VSM, and Dirichlet. Enter C for Project 3 and a comparison of query reduction
	and expansion techniques. Enter Q when you are prepared to quit the progam.

	If the user selects P (Project 3 Option) the program will run 8 tests and output the results in two tables. 
	The first table contains the results of query expansion and reduction as run against the single index. The second
	table contains the results of the query expansion and reduction as run against the stem index. 

*** NOTE 1 *** Please be aware that the library used as a Thesaurus, PyDictionary, is a subset of Beautiful Soup. Beautiful Soup has been 
printing a warning when running concerning the html parser used. Should you see this warning, please ignore it as well as the output when 
certain terms do not have a synonym in the API. 

*** NOTE 2 *** The trec_eval executable is currently compiled for a Mac machine. If this is not correct for your system, 
you will need to download the trec_eval source code, make it, and then add the executable to this folder. 

Libraries Required:
heapq
time
math
OrderedDict
itemgetter
commands
Texttables
re
datetime
nltk
PorterStemmer
statistics
heapq
os
PyDictionary (https://pypi.python.org/pypi/PyDictionary/1.3.4)

