import unittest
import doccu_server as doccu

class MyAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = doccu.app.test_client()

    def test_home_title(self):
        """Test that the homepage calls itself Doccu - Home"""
        rv = self.app.get('/')
        self.assertIn('<title>Doccu - Home</title>'.encode('utf-8'), rv.data)

    def test_home_search(self):
        """Test that the homepage has a search function"""
        rv = self.app.get('/')
        self.assertIn('<form action="/search/" method="POST">'.encode('utf-8'), rv.data)

    def test_home_categories(self):
        """Test that the homepage lists categories"""
        rv = self.app.get('/')
        self.assertIn('<h1>Categories:</h1>'.encode('utf-8'), rv.data)

    def test_search_page(self):
        """Test that the search page is accessible"""
        assert False

    def test_search_submit(self):
        """Test that the search page is useable"""
        assert False

    def test_new_document(self):
        """Test that you can create a new document"""
        assert False

    def test_read_document(self):
        """Test that you can read a document"""
        assert False

    def test_read_document_markdown(self):
        """Test that Markdown turns into HTML correctly"""
        assert False

    def test_approve_document(self):
        """Test that you can approve a document"""
        assert False

    def test_expire_check_document(self):
        """Test that documents expire correctly"""
        assert False
