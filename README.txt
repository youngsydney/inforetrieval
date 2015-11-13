READ_ME

Sydney Young
November 13, 2015
COSC 488: Introduction to Information Retrieval

How to Run: 
	On the command line -- navigate to the project directory and type "python run.py"
	Compile and run the run.py file. The method controls preprocessing, indexing, and query processing. 

*** NOTE *** The trec_eval executable is currently compiled for a Mac machine. If this is not correct for your system, 
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

The program will output to the screen the reports on the query processing MAP scores and times by Retrieval Model. 

Optional:
If you would like to test the effect of the query length on MAP, you can look at line 53 in run.py, change 'title' to 'desc' or 'narr' 
	to see how the results change depending on the length of the query.