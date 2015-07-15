import unittest
import os
import doccu_server as doccu
import piedown

class MyAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = doccu.app.test_client()

    def test_travis_setup_exists(self):
        """Test that Travis CI's setup file exists"""
        if os.path.isfile('travis-setup.py'):
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
        self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        rv = self.app.post('/search/',data={'category':'testing','title':'','author':''})
        self.assertIn('<h3>Categories Found for TESTING:</h3>'.encode('utf-8'), rv.data)

    def test_read_document(self):
        """Test that you can read a document"""
        self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        rv = self.app.get('document/0.Automated_Test/')
        self.assertIn('<h2>Document: Automated Test</h2>'.encode('utf-8'), rv.data)

    def test_read_document_markdown(self):
        """Test that Markdown turns into HTML correctly"""
        self.app.post('/document/new/new/', data = {'title':'Automated Markdown Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'# Title\n\n##Subtitle\n\n###Tagline\n\n* Bullet point\n\n*Italic*\n\n**Bold**\n\n***Both italic and bold***','identifier':'223344997766551100'})
        rv = self.app.get('/document/0.Automated_Markdown_Test/')
        self.assertIn('<h3>Document Proper:</h3>\n<h1>Title</h1>\n<h2>Subtitle</h2>\n<h3>Tagline</h3>\n<ul>\n<li>Bullet point</li>\n</ul>\n<p><em>Italic</em></p>\n<p><strong>Bold</strong></p>\n<p><strong><em>Both italic and bold</em></strong></p>', rv.data)

    def test_approve_document(self):
        """Test that you can approve a document"""
        self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        rv = self.app.post('document/0.Automated_Test/approve/', data={'version':'0','date':'2020-08-08','date-renew':'2021-08-08','identifier':'223344997766551100'})
        self.assertIn('Form submitted for', rv.data)

    def test_expire_check_document(self):
        """Test that documents expire correctly"""
        self.app.post('document/0.Automated_Test/approve/', data={'version':'0','date':'1992-08-08','date-renew':'1993-08-08','identifier':'223344997766551100'})
        rq = self.app.get('/document/0.Automated_Test/')
        self.assertIn('not active', rq.data)

    def test_piedown(self):
        """Test the Piedown renders Markdown into HTML correctly"""
        if piedown.render('#Title') == '<h1>Title</h1>':
            if piedown.render('##Subtitle') == '<h2>Subtitle</h2>':
                if piedown.render('###Tagline') == '<h3>Tagline</h3>':
                    if piedown.render('*Italic*') == '<p><em>Italic</em></p>':
                        if piedown.render('**Bold**') == '<p><strong>Bold</strong></p>':
                            if piedown.render('***Both italic and bold***') == '<p><strong><em>Both italic and bold</strong></em></p>':
                                if piedown.render('* Bullet point') == '<ul>\n<li>Bullet point</li>\n</ul>':
                                    pass
                            else:
                                assert False
                        else:
                            assert False
                    else:
                        assert False
                else:
                    assert False
            else:
                assert False
        else:
            assert False

    def test_view_category(self):
        """Test that Categories display their contents correctly"""
        rv = self.app.get('category/testing/')
        self.assertIn('<li>', rv.data)

    def test_access_denied(self):
        """Test that the access denied page is accessible"""
        rv = self.app.get('/accessdenied')
        self.assertIn('Access Denied', rv.data)

    def test_access_denied_edit(self):
        """Test that editing a page without the correct ID fails"""
        self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        rv = self.app.post('/document/0.Automated_Test/edit/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'0000'})
        self.assertIn('accessdenied', rv.data)

    def test_access_denied_approve(self):
        """Test that approving a page without the correct ID fails"""
        self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        rv = self.app.post('/document/0.Automated_Test/approve/', data={'version':'0','date':'2020-08-08','date-renew':'2021-08-08','identifier':'0000'})
        self.assertIn('accessdenied', rv.data)

    def test_access_denied_create(self):
        """Test that creating a new document without the correct ID fails"""
        self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'223344997766551100'})
        rv = self.app.post('/document/new/new/', data = {'title':'Automated Test','category':'testing','descriptor':'This is an automated testing procedure.','preamble':'This is an automated testing procedure','document-proper':'This is n automated testing procedure','identifier':'0000'})
        self.assertIn('accessdenied', rv.data)

    def test_log_exists(self):
        """Test that the log file is correctly created"""
        self.app.get('/random/long/string/that/fails')
        if os.path.isfile('error.log'):
            pass
        else:
            assert False