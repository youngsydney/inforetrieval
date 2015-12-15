import index
import constant
import myHTMLParser
import re
from datetime import datetime
import nltk
from nltk.stem import PorterStemmer


def read_collection(file_path):
	"""This function takes a single file and returns a list of strings. Each
	string is a document (between opening and closing <DOC> tags."""

	with open(file_path, 'r') as wholeFile:
		text = wholeFile.read()
		text = text.replace('</DOC>', '</DOC> BREAK_NEW_DOC')
		documents = text.split('BREAK_NEW_DOC')
	return documents


def get_docID(text):
	"""This function returns the docID."""

	h = myHTMLParser.myHTMLParser()
	h.feed(text)
	return h.returnDocID()

def get_text(text):
	"""This function returns the text in a document and 
	excludes tags and comments."""

	h = myHTMLParser.myHTMLParser()
	h.feed(text)
	return h.returnFiltered()

	
def processing(document, indexType):
	"""This function controls the processing. It sends each token 
	through the various functions that handle the different cases. 
	At the end, it does the same for any hyphenated words that had
	been split up and need to be processed individually."""

	caughtTokens = []
	moreCaught = []
	text = get_text(document)
	text = text.lower()
	text = dates(text, indexType)
	text = split_special_char(text, indexType)
	tokens = split_on_spaces(text)
	for idx, token in enumerate(tokens):
		tokens[idx],caughtTokens = hyphens(tokens[idx], indexType)
		tokens[idx],moreCaught = underscore(tokens[idx], indexType)
		tokens[idx] = processing_steps(tokens[idx], indexType)
	caughtTokens.append(moreCaught)
	if caughtTokens:
		for idx, needtoadd in enumerate(caughtTokens):
			if type(needtoadd) == 'string':
				caughtTokens[idx] = processing_steps(caughtTokens[idx], indexType)
				tokens.append(caughtTokens[idx])
	tokens = delete_empty(tokens)
	if indexType == 'positional':
		return tokens
	elif indexType == 'stem':
		tokens = removeStop(tokens)
		tokens = stem_terms(tokens)
		return tokens
	elif indexType == 'phrase':
		tokens = build_phrases(tokens)
		return tokens
	else:
		tokens = removeStop(tokens)
		return tokens

def processing_steps(token, indexType):
	"""This function handles passing an individual token
	to every function to be processed."""

	token = file_extensions(token, indexType)
	token = extra_zeros(token, indexType)
	token = start_of_heading(token, indexType)
	token = remove_nums(token, indexType)
	token = currency(token, indexType)
	token = period_end(token, indexType)
	token = periods(token, indexType)
	return token


def remove_nums(token, indexType):
	"""This function removes any tokens containing non-alpha
	characters from the stem and the phrase index."""

	if indexType == 'stem' and not token.isalpha():
		return ''
	elif indexType == 'phrase' and not token.isalpha():
		return ' STOP '
	else:
		return token


def file_extensions(token, indexType):
	"""This function deletes the period from file extensions, unless
	it is processing for a stem of phrase index in which cases the token
	is removed."""

	if re.search(constant.file_ext, token):
		if indexType=='phrase':
			token=re.sub(constant.file_ext, ' STOP ', token)
		elif indexType=='stem':
			token=''
		else:
			token=re.sub(constant.file_ext, r'\1\2', token)
	return token


def currency(token, indexType):
	"""This function handles processing for tokens involving the $ 
	and also handles extra zeros in currency. """

	if re.search(constant.currency, token):
		if indexType == 'phrase':
			token = ' STOP '
		elif indexType == 'stem':
			token = ''
		else:
			if len(token) == 1:
				token = ''
			elif '.' not in token:
					token = token
			else:
				cents = token.split('.', 2)
				if len(cents[1]) == 1:
					if cents[1] == '0':
						token = cents[0]
					else:
						token = token
				elif len(cents[1]) == 2:
					if cents[1] == '00':
						token = cents[0]
					elif cents[1][1] == '0':
						token = (cents[0] + '.' + cents[1][0])
					else:
						token = (cents[0] + '.' + cents[1][0] + cents[1][1])
				elif len(cents[1]) == 3:
					if cents[1] == '000':
						token = cents[0]
					else:
						token = token
				elif not cents[1]:
					token = cents[0]
	if re.search(constant.currency_zerovalue, token):
		token = ''
	return token


def hyphens(token, indexType):
	"""This function splits the token into pieces, deletes 
	hyphens, etc. depending on the type of index."""

	needtoadd = []
	if '-' in token:
		if indexType == 'phrase':
			token = ' STOP ' 
		if indexType == 'single' or indexType == 'positional':
			token = re.sub('-', '', token)
		if indexType == 'single' or indexType == 'stem':
			pieces = token.split('-')
			for piece in pieces:
				if len(piece) >= 3:
					needtoadd.append(piece)
	else:
		token = token
	return token, needtoadd


def extra_zeros(token, indexType):
	"""This function deals with the extra zeros in numbers
	in order to normalize numbers for indexing. In the case of 
	the stem index, the token is deleted. In the case of the phrase 
	it is marked as a break (STOP). """

	if re.search(constant.numerical_leading_zeros, token):
		if indexType == 'stem':
			token = ''
		elif indexType == 'phrase':
			token = ' STOP '
		else:
			token = re.sub(constant.numerical_leading_zeros, '', token)
	if re.search(constant.numerical_trailing_zeros, token):
		if indexType == 'stem':
			token = ''
		elif indexType == 'phrase':
			token = ' STOP '
		else:
			token = re.sub(constant.numerical_trailing_zeros, r'\1', token)
	if token == '0' or token == '00' or token == '000':
		token = ''
	return token


def start_of_heading(token, indexType):
	"""This removes any SOH errors that can be generated during parsing."""

	token = re.sub(constant.start_of_heading, '', token)
	return token


def underscore(token, indexType):
	"""This function handles underscores (except those in date form) in terms the
	same way it would handle hypens."""

	needtoadd = []
	if '_' in token: 
		if not re.search(constant.date_format, token):
			if indexType == 'phrase':
				token = ' STOP ' 
			if indexType == 'single' or indexType == 'positional':
				token = re.sub('_','', token)
			if indexType == 'single' or indexType == 'stem':
				pieces = token.split('_')
				for piece in pieces:
					if len(piece) >= 3:
						needtoadd.append(piece)
		else:
			token = token
	return token, needtoadd



def dates(text, indexType): 
	"""This function identifies dates, checkes them for validity,
	and then puts them in a consistent format. """

	matchedDate1 = re.findall(constant.date1, text)
	for obj in matchedDate1:
		if indexType == 'phrase':
			text = re.sub(constant.date1, ' STOP ', text)
		else:
			try:
				dt = datetime.strptime(obj,'%m/%d/%Y')
				text = re.sub(obj,(dt.strftime(' %B_%d_%Y')),text)
			except:
				obj = obj
	matchedDate2 = re.findall(constant.date2, text)
	for obj in matchedDate2:
		if indexType == 'phrase':
			text = re.sub(constant.date1, ' STOP ', text)
		else:
			try:
				dt = datetime.strptime(obj,'%m-%d-%Y')
				text = re.sub(obj,(dt.strftime(' %B_%d_%Y')),text)
			except:
				obj = obj
	matchedDate3 = re.findall(constant.date3, text)
	for obj in matchedDate3:
		if indexType == 'phrase':
			text = re.sub(constant.date1, ' STOP ', text)
		else:
			try:
				dt = datetime.strptime(obj,'%B %d, %Y') 
				text = re.sub(obj,(dt.strftime(' %B_%d_%Y')),text)
			except:
				obj = obj
	matchedDate4 = re.findall(constant.date4, text)
	for obj in matchedDate4:
		if indexType == 'phrase':
			text = re.sub(constant.date1, ' STOP ', text)
		else:
			try:
				dt = datetime.strptime(obj,'%m-%d-%Y')
				text = re.sub(obj,(dt.strftime(' %B_%d_%Y')),text)
			except:
				obj = obj
	return text


def periods(token, indexType):
	"""End of sentence periods have already been handled. This handles
	emails, urls, ips, abbrevs, and alpha period combos. It deletes/STOP 
	for stem and phrase because tokens with periods are either special 
	cases that should be ignored for phrases or will not be helpful in the
	stemmer."""
	if '.' in token:
		if indexType == 'phrase':
			token = ' STOP '
		if indexType == 'stem':
			token = ''
		elif re.findall(constant.email, token):
			return token
		elif re.findall(constant.url, token):
			return token
		elif re.findall(constant.ip, token):
			return token
		elif re.findall(constant.abbrev, token):
			token = re.sub(constant.abbrev, r'\1', token)
	if '.' in token:
			token = re.sub(constant.period_alpha, r'\1', token)
	return token

def period_end(token, indexType):
	if token:
		if token[len(token)-1] == '.':
			token = token[0:len(token)-1]
		else:
			token = token
	return token

def delete_empty(tokens):
	tokens = [token for token in tokens if token]
	return tokens



def split_special_char(text, indexType):
	"""This function precedes the split on spaces and adds spaces where they are 
	special characters in order to draw out the valid tokens before processing."""

	if indexType == 'phrase':
		text = re.sub(constant.specialChar, ' STOP ', text)
	else:
		text = re.sub(constant.specialChar, ' ', text)
	return text


def split_on_spaces(text):
	"""This function splits the string on spaces to return a list of individual
	tokens to be processed."""

	tokens = text.split()
	return tokens


def removeStop(tokens):
	"""This method removes the 
	stop words from the list of tokens."""

	stopWords = make_list_stops()
	for idx, token in enumerate(tokens):
		if token in stopWords:
			tokens[idx] = ''
	tokens = delete_empty(tokens)
	return tokens


def make_list_stops():
	"""This compiles the list of stop words and returns."""

	with open('stops.txt') as stopFile:
		stops = stopFile.read()
		stops = stops.replace('\'', '')
		stopWords = stops.split()
		return stopWords


def stem_terms(tokens):
	"""This function uses the Porter Stemmer to stem each of the 
	tokens and returns a list with the stemmed results. """

	stemmer = PorterStemmer()
	stemmed = []
	for token in tokens:
		try:
			stemmed.append(str(stemmer.stem(token)))
		except:
			stemmed.append('')
	stemmend = delete_empty(stemmed)
	return stemmed


def build_phrases(tokens):
	"""This function iterates through the tokens
	to build a list of the 2-word and 3-word phrases."""

	stopWords = make_list_stops()
	special_case = 'STOP'
	string_2 = ''
	string_3 = ''
	num_terms = 0
	phrases = []

	for idx, word in enumerate(tokens):
		if word not in stopWords and 'STOP' not in word:
			if num_terms == 0:
				string_2 += word
			elif num_terms ==1:
				string_2 += ' ' + word
			elif num_terms == 2:
				string_2 += ' ' + word
				string_3 += ' ' + word 
			num_terms+=1
		elif word in stopWords or 'STOP' in word:
			if num_terms == 1:
				string_2 = ''
				num_terms = 0
			elif num_terms == 2:
				phrases.append(string_2)
				string_2 = ''
				num_terms = 0

		if num_terms == 2:
			phrases.append(string_2)
			string_3 = string_2
			string_2 = string_2.split(' ')[1]
			num_terms = 2
		elif num_terms == 3:
			phrases.append(string_3)
			phrases.append(string_2)
			string_3 = ''
			string_2 = string_2.split(' ')[1]
			num_terms = 1
	if ' ' in string_2:
		phrases.append(string_2)
	return phrases

