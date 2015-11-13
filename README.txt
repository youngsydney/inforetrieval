READ_ME

Sydney Young
November 13, 2015
COSC 488: Introduction to Information Retrieval

How to Run: 
	Compile and run the run.py file. In the run.py file there is a main method which controls the processing and indexing of all the documents. 
	Note: Set the memory constraint at the top of the indexer.py and the file path for the folder where the date files are kept at the top of the run.py

The output to the screen will be the execution time for the various indexes. The lexicon/posting list is stored in the indexType_out_path and the term list with document frequencies is stored in the indexType_terms. 


term index = {term:docFreq, term:docFreq}
lexicon = {termID: {docID:tf, docID:tf}, termID: {docID:tf}} 
lexicon_positional = {termID: {docID:[pos, pos, pos]}, termID: {docID:[pos]}} 

Notes about processing:
	For the phrase index, special cases get replaced with " STOP " so during the phrase identification stage the phrases can't cross over special cases.
	For the cases of hyphenated words, I merged the word (black-tie became blacktime) and only stored the combined in the positional index. 

