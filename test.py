import unittest
import os
import doccu_server as doccu

class MyAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = doccu.app.test_client()

    def test_travis_configuration_exists(self):
        """Test that Travis CI's configuration file exists"""
        if os.path.isfile('.travis.yml'):
            pass
        else:
            assert False

    def test_travis_setup_exists(self):
        """Test that Travis CI's setup file exists"""
        if os.path.isfile('travis-static.py'):
            pass
        else:
            assert False

    def test_travis_running(self):
        """Test that running on Travis CI is detected"""
        if os.getenv('TRAVIS'):
            pass
        else:
            assert False

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
        rv = self.app.get('/search/')
        self.assertIn('<form action="/search/" method="POST">'.encode('utf-8'), rv.data)

    def test_new_document(self):
        """Test that you can create a new document"""
        rv = self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        self.assertIn('Form submitted for'.encode('utf-8'), rv.data)

    def test_search_submit(self):
        """Test that the search page is useable"""
        rv = self.app.post('/search/',data={'category':'testing','title':'','author':''})
        self.assertIn('<h3>Categories Found for TESTING:</h3>'.encode('utf-8'), rv.data)

    def test_read_document(self):
        """Test that you can read a document"""
        rv = self.app.get('document/0.Automated_Test/')
        self.assertIn('<h2>Document: Automated Test</h2>'.encode('utf-8'), rv.data)

    def test_read_document_markdown(self):
        """Test that Markdown turns into HTML correctly"""
        assert False

    def test_approve_document(self):
        """Test that you can approve a document"""
        assert False

    def test_expire_check_document(self):
        """Test that documents expire correctly"""
        assert False

    def test_sendmail_new(self):
        """Test that emails are sent at document creation"""
        assert False

    def test_piedown(self):
        """Test the Piedown renders Markdown into HTML correctly"""
        assert False

    def test_view_category(self):
        """Test that Categories display their contents correctly"""
        assert False

    def test_access_denied(self):
        """Test that the access denied page is accessible"""
        rv = self.app.get('/accessdenied')
        self.assertIn('Access Denied', rv.data)

    def test_access_denied_edit(self):
        """Test that editing a page without the correct ID fails"""
        assert False

    def test_access_denied_approve(self):
        """Test that approving a page without the correct ID fails"""
        assert False

    def test_access_denied_create(self):
        """Test that creating a new document without the correct ID fails"""
        assert False

    def test_log_exists(self):
        """Test that the log file is correctly created"""
        self.app.get('/random/long/string/that/fails')
        if os.path.isfile('error.log'):
            pass
        else:
            assert False