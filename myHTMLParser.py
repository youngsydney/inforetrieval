from HTMLParser import HTMLParser

class myHTMLParser(HTMLParser):

	def __init__(self):
		HTMLParser.__init__(self)
		self.filtered=''
		self.flagForReturn=False
		self.state=''
		self.docID=''

	def handle_data(self, data):
		if self.state=='docno':
			self.docID=data.replace(' ','')
		elif self.state!='parent':
			self.filtered+=data

	def handle_starttag(self,tag,attr):
		self.state=tag

	def handle_endtag(self, tag):
		self.state=''

	def returnFiltered(self):
		return self.filtered

	def returnDocID(self):
		return self.docID
