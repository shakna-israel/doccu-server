# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, redirect
import glob
import logging
import markdown
from os.path import expanduser
import os
import jinja2
import time
import base64
import piedown
import re
import sendmail
from lib import get_ip_address
import json

if os.getenv('Doccu', 'Development') == 'Production':
    doccu_static = expanduser('~/.doccu/static')
    doccu_templates = expanduser('~/.doccu/templates')
else:
    doccu_static = expanduser('~/.doccu/static')
    doccu_templates = expanduser('~/doccu-templates')
app = Flask(__name__,static_folder=doccu_static)

template_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(doccu_templates),
])
app.jinja_loader = template_loader

@app.route("/")
@app.route("/<name>/")
def home(name="None"):
    doccu_docs = expanduser("~/.doccu/documents")
    databases = glob.glob(doccu_docs + '/*.db')
    policy = {}
    for database in databases:
        document = json.load(open(database, "r"))
        database_url = str(database.replace(".db",'').replace(doccu_docs + '/',''))
        policy_title = document['title']
        try:
            if int(document['version']) > int(policy[policy_title]['version']):
                policy[policy_title] = {'title':policy_title, 'url': database_url, 'version': document['version']}
        except KeyError:
            policy[policy_title] = {'title':policy_title, 'url': database_url, 'version': document['version']}
    categories = []
    for database in databases:
        document = json.load(open(database, "r"))
        categories.extend(document['category'])
    categories = sorted(list(set(categories)))
    try:
        policy_title = sorted(list(set(policy_title)),reverse=True)
    except UnboundLocalError:
        policy_title="None"
    if not databases:
        return render_template('index.html',policies={"None": {"url":""}},categories=["None"],title="Home")
    else:
        return render_template('index.html',policies=policy,categories=categories,title="Home")

@app.route("/search/", methods=['GET','POST'])
def search():
    if request.method == 'GET':
        return render_template('get_search.html',title='Search')
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        author = request.form['author']
        search_for_categories = search_categories(category)
        categories_found = search_for_categories['found']
        search_categories_list = search_for_categories['search']
        try:
            for item in search_categories_list:
                try:
                    searched_categories = str(item).upper() + ', ' + searched_categories
                except UnboundLocalError:
                    searched_categories = str(item).upper()
        except TypeError:
            search_categories_list = False
            searched_categories = False
        titles_found = search_titles(title)['found']
        try:
            titles_search = search_titles(title)['search'].upper()
        except AttributeError:
            titles_search = False
        authors_found = search_authors(author)['found']
        try:
            search_author = search_authors(author)['search'].upper()
        except AttributeError:
            search_author = False

        if (author and category and title):
            both_titles_and_authors = False
            author_and_category = False
            category_and_title = False
            triple_filter = { 'list':list(set(titles_found).intersection(authors_found)), 'category':category}
        elif (author and title):
            both_titles_and_authors = list(set(titles_found).intersection(authors_found))
            author_and_category = False
            category_and_title = False
            triple_filter = False
        elif (category and title):
            both_titles_and_authors = False
            author_and_category = False
            category_and_title = { 'list': titles_found, 'category': category}
            triple_filter = False

        elif (author and category):
            both_titles_and_authors = False
            author_and_category = { 'list': authors_found, 'category': category}
            category_and_title = False
            triple_filter = False
        else:
            both_titles_and_authors = False
            author_and_category = False
            category_and_title = False
            triple_filter = False

        return render_template('search_out.html',categories=categories_found,categories_search=searched_categories,titles_found=titles_found,titles_search=titles_search,authors_found=authors_found,search_author=search_author,title="Search",both_titles_and_authors=both_titles_and_authors,triple_filter=triple_filter,author_and_category=author_and_category,category_and_title=category_and_title)

def search_categories(category):
    if category == '':
        category = False
    try:
        categories = category.split(",")
    except AttributeError:
        categories = False
    try:
        for category in categories:
            category = category.strip()
    except TypeError:
        categories = False

    doccu_docs = expanduser("~/.doccu/documents")
    databases = glob.glob(doccu_docs + '/*.db')
    categories_found = {}
    try:
        for category in categories:
            for database in databases:
                document = json.load(open(database, "r"))
                for item in document['category']:
                    if category.lower() in item.lower():
                        categories_found[item] = item
    except TypeError:
        categories_found = False
    return {'found':categories_found,'search':categories}

def search_titles(title):
    if title == '':
        title = False
    doccu_docs = expanduser("~/.doccu/documents")
    databases = glob.glob(doccu_docs + '/*.db')
    titles_found = {}
    for database in databases:
        document = json.load(open(database, "r"))
        try:
            if title.lower() in document['title'].lower():
                titles_found[document['title']] = { 'title': document['title'], 'version': document['version'], 'category': document['category'] }
        except AttributeError:
            titles_found = False
    return {'found':titles_found,'search':title}

def search_authors(author):
    if author == '':
        author = False
    doccu_docs = expanduser("~/.doccu/documents")
    databases = glob.glob(doccu_docs + '/*.db')
    authors_found = {}
    for database in databases:
        document = json.load(open(database, "r"))
        try:
            if author.lower() in document['userid'].lower():
                try:
                    if authors_found[document['title']]:
                        if int(document['version']) > int(authors_found[document['title']]['version']):
                            authors_found[document['title']] = { 'title': document['title'], 'version': document['version'], 'category': document['category'] }
                    else:
                        authors_found[document['title']] = { 'title': document['title'], 'version': document['version'], 'category': document['category'] }
                except KeyError:
                    authors_found[document['title']] = { 'title': document['title'], 'version': document['version'], 'category': document['category'] }
        except AttributeError:
            authors_found = False
    return {'found':authors_found,'search':author}

@app.route("/category/<name>/")
def show_category(name):
    doccu_docs = expanduser("~/.doccu/documents")
    databases = glob.glob(doccu_docs + '/*.db')
    policy = {}
    for database in databases:
        document = json.load(open(database, "r"))
        if name in document['category']:
            policy_title = document['title']
            database_url = str(database.replace(".db",'').replace(doccu_docs + '/',''))
            try:
                if int(document['version']) > int(policy[policy_title]['version']):
                    policy[policy_title] = {'title':policy_title, 'url': database_url, 'version': document['version']}
            except KeyError:
                policy[policy_title] = {'title':policy_title, 'url': database_url, 'version': document['version']}
    return render_template('category.html',name=name, policies=policy,title="Category: " + str(name))

@app.route("/document/<name>/")
def document_fetch(name):
    doccu_docs = expanduser('~/.doccu/documents')
    doccu_img = expanduser("~/.doccu/static/img")
    document_name = doccu_docs + "/" + str(name) + ".db"
    unversioned_name = name.split('.', 1)[-1]
    old_versions_docs = sorted(glob.glob(doccu_docs + '/*' + unversioned_name + '*.db'))
    old_versions = {}
    for item in old_versions_docs:
        ver = 'v' + item.replace(doccu_docs + '/',"").replace('.db','').split('.',1)[0]
        path = '/document/' + item.replace(".db","").replace(doccu_docs + '/',"")
        old_versions[item] = {'ver':ver,'path':path}
    if os.path.exists(doccu_img + "/logo.jpg"):
        logo = "/static/img/logo.jpg"
        logo_path = doccu_img + "/logo.jpg"
    elif os.path.exists(doccu_img + "/logo.png"):
        logo = "/static/img/logo.png"
        logo_path = doccu_img + "/logo.png"
    else:
        logo = False
    if logo:
        with open(logo_path, 'rb') as logo_file:
            logo_base64 = base64.b64encode(logo_file.read())
            logo_file.close()
    else:
        logo_base64 = False
    try:
        document = json.load(open(document_name, "r"))
    except IOError:
        return redirect('/')
    title = document['title']
    try:
        document['date']
        date = document['date']
    except KeyError:
        date = "InActive"
    userid = document['userid'].upper()
    try:
        document['date-renew']
        renew_date = document['date-renew']
    except KeyError:
        renew_date = "InActive"
    current_date = str(time.strftime("%Y/%m/%d"))
    version = document['version']
    category = document['category']
    descriptor = document['descriptor'].replace('\r\n',' ')
    descriptor = markdown.markdown(descriptor)
    descriptor_json = document['descriptor'].replace('\r\n',' ').replace("'","\\'")
    preamble = document['preamble'].replace('\r\n',' ')
    preamble = markdown.markdown(preamble)
    preamble_json = document['preamble'].replace('\r\n',' ').replace("'","\\'")
    content = document['content']
    content_json = document['content']
    content_json = [w.replace('"', "''") for w in content_json]
    markdown_json = []
    for item in content_json:
        item = piedown.render(item)
        item = item
        markdown_json.append(item)
    markdown_json = [w.replace('\n', "") for w in markdown_json]
    content_json = markdown_json
    content_markdown = ""
    for line in document['content']:
        content_markdown = content_markdown + "\n" + line
    content_markdown = markdown.markdown(content_markdown)
    for item in content_json:
        item = item.replace("'","\\'")
    path = request.path
    return render_template('document.html',title=title,date=date,renew_date=renew_date,current_date=current_date,version=version,category=category,content=content,descriptor=descriptor,preamble=preamble,descriptor_json=descriptor_json,preamble_json=preamble_json,content_json=content_json,file=name,userid=userid,path=path,content_markdown=content_markdown,logo=logo,logo_base64=logo_base64,re=re,old_versions=old_versions,reversed=reversed,sorted=sorted,open=open,base64=base64,expanduser=expanduser)

@app.route('/accessdenied')
def access_denied():
    return render_template("new_document_denied.html",title="Access Denied")

@app.route("/document/<name>/edit/", methods=['GET','POST'])
def document_edit(name):
    if request.method == 'GET':
        doccu_docs = expanduser("~/.doccu/documents")
        document_name = doccu_docs + "/" + str(name) + ".db"
        try:
            document = json.load(open(document_name, "r"))
        except IOError:
            return redirect('/')
        title = document['title']
        try:
            date = document['date']
        except KeyError:
            date = "InActive"
        try:
            renew_date = document['date-renew']
        except KeyError:
            renew_date = "InActive"
        category = document['category']
        categories = ""
        for item in category:
            categories = item + ", " + categories
        descriptor = document['descriptor'].replace('\r\n',' ')
        preamble = document['preamble'].replace('\r\n',' ')
        version = document['version']
        content = document['content']
        content_html = ""
        for item in content:
            content_html = content_html + item + "\n"
        return render_template('edit_document.html',title=name,date=date,renew_date=renew_date,category=categories,descriptor=descriptor,preamble=preamble,content=content_html,version=version,old_versions=False)
    if request.method == 'POST':
        doccu_home = expanduser('~/.doccu')
        doccu_docs = expanduser('~/.doccu/documents')
        title = name
        title = title.split('.')[-1]
        title = title.replace("_"," ")
        identifier = request.form['identifier']
        auth_db = json.load(open(doccu_home + "/ids.dbs", "r"))

        for key in auth_db.keys():
            if str(identifier) == str(auth_db[key]['key']):
                if auth_db[key]['group'] == 'superadmin':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
                elif auth_db[key]['group'] == 'admin':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
                elif auth_db[key]['group'] == 'editor':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
        try:
            document['userid']
            if userid not in document['userid']:
                userid = userid + ', ' + document['userid']
        except NameError:
            try:
                userid = userid
            except NameError:
                return redirect('/accessdenied')
        try:
            userid
        except NameError:
            return redirect('/accessdenied')
        date = 'InActive'
        renew_date = 'InActive'
        categories = request.form['category']
        category = categories.split(',')
        category = [item.strip(' ') for item in category]
        descriptor = request.form['descriptor']
        preamble = request.form['preamble']
        proper = request.form['document-proper']
        version = request.form['version']
        version = str(int(version) + 1)
        content = []
        for line in proper.split('\n'):
            line = line.replace('\r','')
            content.append(line)
        dict_to_store = {'title':title,'date':date,'date-renew':renew_date,'category':category,'descriptor':descriptor,'preamble':preamble,'content':content,'version':version,'userid':userid}
        filename = doccu_docs + "/" + str(version) + "." + str(title).replace(" ", "_") + ".db"
        json.dump(dict_to_store,open(filename,"w+"), sort_keys=True, indent=4, separators=(',', ': '))
        filename = filename.replace(".db",'').replace(doccu_docs,"").replace("/","")
        ip_address = get_ip_address()
        for key in auth_db.keys():
            if str(auth_db[key]['group']) == 'admin':
                sendmail.send_email(str(auth_db[key]['email']),str(key).upper(),'Edited Document awaiting approval: [' + name + '](http://' + ip_address + '/document/' + name + ')')
            elif str(auth_db[key]['group']) == 'superadmin':
                sendmail.send_email(str(auth_db[key]['email']),str(key).upper(),'Edited Document awaiting approval: [' + name + '](http://' + ip_address + '/document/' + name + ')')
        return render_template('new_document_submitted.html',filename=str(filename),title=title, old_versions=False)

@app.route("/document/<name>/approve/", methods=['GET','POST'])
def document_approve(name):
    if request.method == 'GET':
        doccu_docs = expanduser("~/.doccu/documents")
        document_name = doccu_docs + "/" + str(name) + ".db"
        try:
            document = json.load(open(document_name, "r"))
        except IOError:
            return redirect('/')
        title = document['title']
        try:
            date = document['date']
        except KeyError:
            date = "InActive"
        try:
            renew_date = document['date-renew']
        except KeyError:
            renew_date = "InActive"
        version = str(name).split('.')[0]
        return render_template('approve_document.html',title=name,date=date,renew_date=renew_date,version=version,old_versions=False)
    if request.method == 'POST':
        doccu_home = expanduser('~/.doccu')
        doccu_docs = expanduser('~/.doccu/documents')
        document_name = doccu_docs + "/" + str(name) + ".db"
        try:
            document = json.load(open(document_name, "r"))
        except IOError:
            return redirect('/')
        title = name
        title = title.split('.')[-1]
        title = title.replace("_"," ")
        identifier = request.form['identifier']
        auth_db = json.load(open(doccu_home + "/ids.dbs", "r"))
        for key in auth_db.keys():
            if str(identifier) == str(auth_db[key]['key']):
                if auth_db[key]['group'] == 'superadmin':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
                elif auth_db[key]['group'] == 'admin':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
        try:
            document['userid']
            if userid not in document['userid']:
                userid = userid + ', ' + document['userid']
        except NameError:
            try:
                userid = userid
            except NameError:
                return redirect('/accessdenied')
        try:
            userid
        except NameError:
            return redirect('/accessdenied')
        date = request.form['date'].strip()
        renew_date = request.form['date-renew'].strip()
        category = document['category']
        descriptor = document['descriptor']
        preamble = document['preamble']
        content = document['content']
        version = request.form['version']
        version = str(int(version) + 1)
        dict_to_store = {'title':title,'date':date,'date-renew':renew_date,'category':category,'descriptor':descriptor,'preamble':preamble,'content':content,'version':version,'userid':userid}
        filename = doccu_docs + "/" + str(version) + "." + str(title).replace(" ", "_") + ".db"
        json.dump(dict_to_store,open(filename,"w+"), sort_keys=True, indent=4, separators=(',', ': '))
        filename = filename.replace(".db",'').replace(doccu_docs,"").replace("/","")
        return render_template('new_document_submitted.html',filename=str(filename),title=title,old_versions=False)

@app.route("/document/new/<name>/", methods=['GET','POST'])
def document_new(name):
    if request.method == 'GET':
        if name == 'json':
            return redirect('/')
        return render_template('new_document.html',title="New Document",old_versions=False)
    if request.method == 'POST':
        doccu_home = expanduser('~/.doccu')
        identifier = request.form['identifier']
        auth_db = json.load(open(doccu_home + "/ids.dbs", "r"))

        for key in auth_db.keys():
            if str(identifier) == str(auth_db[key]['key']):
                if auth_db[key]['group'] == 'superadmin':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
                elif auth_db[key]['group'] == 'admin':
                    userid = str(key) + ' (' + str(auth_db[key]['group']) + ')'
        try:
            userid
        except NameError:
            return redirect('/accessdenied')

        title = request.form['title'].strip()
        categories = request.form['category']
        category = categories.split(',')
        category = [item.strip(' ') for item in category]
        descriptor = request.form['descriptor']
        preamble = request.form['preamble']
        proper = request.form['document-proper']
        version = 0
        content = []
        for line in proper.split('\n'):
            line = line.replace('\r','')
            content.append(line)
        dict_to_store = {'title':title,'category':category,'descriptor':descriptor,'preamble':preamble,'content':content,'version':version,'userid':userid}
        doccu_docs = expanduser("~/.doccu/documents")
        filename = doccu_docs + "/" + str(version) + "." + str(title).replace(" ", "_") + ".db"
        json.dump(dict_to_store,open(filename,"w+"),sort_keys=True, indent=4, separators=(',', ': '))
        filename = filename.replace(".db",'').replace(doccu_docs,"").replace("/","")
        ip_address = get_ip_address()
        for key in auth_db.keys():
            if str(auth_db[key]['group']) == 'admin':
                sendmail.send_email(str(auth_db[key]['email']),str(key).upper(),'New Document awaiting approval: [' + name + '](http://' + ip_address + '/document/' + name + ')')
            elif str(auth_db[key]['group']) == 'superadmin':
                sendmail.send_email(str(auth_db[key]['email']),str(key).upper(),'New Document awaiting approval: [' + name + '](http://' + ip_address + '/document/' + name + ')')
        return render_template('new_document_submitted.html',title=title,filename=str(filename),old_versions=False)

if __name__ == "__main__":
    logging.basicConfig(filename='error.log',level=logging.WARNING)
    print("Running on port 5000, logging to error.log")
    app.run(host='0.0.0.0',debug=True)
