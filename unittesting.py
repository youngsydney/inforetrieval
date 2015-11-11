import unittest
import query_process
import preprocess
import index

def AllTests():
	suite = unittest.TestSuite([PreProcessSuite, VSMQuerySuite, BM25QuerySuite])

def PreProcessSuite(unittest.TestSuite):
	suite = unittest.TestLoader().loadTestsFromTestCase(PreprocessUnitTests)
	return suite

def VSMQuerySuite(unittest.TestSuite):
	suite = unittest.TestLoader().loadTestsFromTestCase(QueryVSMUnitTests)
	return suite

def BM25QuerySuite(unittest.TestSuite):
	suite = unittest.TestLoader().loadTestsFromTestCase(QueryBM25UnitTests)
	return suite


class PreprocessUnitTests(unittest.TestCase):
	def setUp(self):
		pass

	def test_process_getDocID(self):
		self.assertEqual(preprocess.get_docID('<DOC><DOCNO>1</DOCNO>hello</DOC>'), '1')

	def test_process_getText(self):
		self.assertEqual(preprocess.get_text('<DOC><DOCNO>1</DOCNO>hello</DOC>'), 'hello')

	def test_process_removeNums(self):
		self.assertEqual(preprocess.remove_nums('5', 'stem'), '')
		self.assertEqual(preprocess.remove_nums('5', 'phrase'), ' STOP ')
		self.assertEqual(preprocess.remove_nums('5', 'single'), '5')
		self.assertEqual(preprocess.remove_nums('5', 'positional'), '5')

	def test_process_fileExt(self):
		self.assertEqual(preprocess.file_extensions('test.pdf', 'stem'), '')
		self.assertEqual(preprocess.file_extensions('test.pdf', 'phrase'), ' STOP ')
		self.assertEqual(preprocess.file_extensions('test.pdf', 'single'), 'testpdf')
		self.assertEqual(preprocess.file_extensions('test.pdf', 'positional'), 'testpdf')

	def test_process_currency(self):
		self.assertEqual(preprocess.currency('$5.0', 'stem'), '')
		self.assertEqual(preprocess.currency('$5.0', 'phrase'), ' STOP ')
		self.assertEqual(preprocess.currency('$', 'single'), '')
		self.assertEqual(preprocess.currency('$67', 'single'), '$67')
		self.assertEqual(preprocess.currency('$67.5', 'single'), '$67.5')
		self.assertEqual(preprocess.currency('$67.0', 'single'), '$67')
		self.assertEqual(preprocess.currency('$67.00', 'single'), '$67')
		self.assertEqual(preprocess.currency('$67.50', 'single'), '$67.5')
		self.assertEqual(preprocess.currency('$67.55', 'single'), '$67.55')
		self.assertEqual(preprocess.currency('$67.000', 'single'), '$67')
		self.assertEqual(preprocess.currency('$67.', 'single'), '$67')





class QueryVSMUnitTests(unittest.TestCase):
	def setUp(self):
		pass

	def test_query_VSM_idf(self):
		self.assertIn('0.176', str(query_process.VSM_idf({'term1': 2 , 'term2': 3}, 3)['term1']))

class QueryBM25UnitTests(unittest.TestCase):
	def setUp(self):
		pass

	def test_query_BM25_weights(self):
		self.assertIn('0.51', str(query_process.BM25_weights({'term1': 2 , 'term2': 3}, 3)['term1']))


if __name__ == '__main__':
   # unittest.main()
	unittest.TextTestRunner(verbosity=2).run(AllTests())







