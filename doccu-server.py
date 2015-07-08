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
try:
    import cpickle
except ImportError:
    import pickle

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
        document = pickle.load(open(database, "rb"))
        database_url = str(database.replace(".db",'').replace(doccu_docs + '/',''))
        policy_title = document['title']
        try:
            if int(document['version']) > int(policy[policy_title]['version']):
                policy[policy_title] = {'title':policy_title, 'url': database_url, 'version': document['version']}
        except KeyError:
            policy[policy_title] = {'title':policy_title, 'url': database_url, 'version': document['version']}
    categories = []
    for database in databases:
        document = pickle.load(open(database, "rb"))
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

@app.route("/category/<name>/")
def show_category(name):
    doccu_docs = expanduser("~/.doccu/documents")
    databases = glob.glob(doccu_docs + '/*.db')
    policy = {}
    for database in databases:
        document = pickle.load(open(database, "rb"))
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
    doccu_docs = expanduser("~/.doccu/documents")
    doccu_img = expanduser("~/.doccu/static/img")
    document_name = doccu_docs + "/" + str(name) + ".db"
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
        document = pickle.load(open(document_name, "rb"))
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
    premable = markdown.markdown(preamble)
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
    return render_template('document.html',title=title,date=date,renew_date=renew_date,current_date=current_date,version=version,category=category,content=content,descriptor=descriptor,preamble=preamble,descriptor_json=descriptor_json,preamble_json=preamble_json,content_json=content_json,file=name,userid=userid,path=path,content_markdown=content_markdown,logo=logo,logo_base64=logo_base64,re=re)

@app.route('/accessdenied')
def access_denied():
    return render_template("new_document_denied.html",title="Access Denied")

@app.route("/document/<name>/edit/", methods=['GET','POST'])
def document_edit(name):
    if request.method == 'GET':
        doccu_docs = expanduser("~/.doccu/documents")
        document_name = doccu_docs + "/" + str(name) + ".db"
        try:
            document = pickle.load(open(document_name, "rb"))
        except IOError:
            return redirect('/')
        title = document['title']
        try:
            date = document['date']
        except KeyError:
            date = "Inactive"
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
        return render_template('edit_document.html',title=name,date=date,renew_date=renew_date,category=categories,descriptor=descriptor,preamble=preamble,content=content_html,version=version)
    if request.method == 'POST':
        doccu_home = expanduser('~/.doccu')
        doccu_docs = expanduser('~/.doccu/documents')
        title = name
        title = title.split('.')[-1]
        title = title.replace("_"," ")
        identifier = request.form['identifier']
        auth_db = pickle.load(open(doccu_home + "/ids.dbs", "rb"))

        for key in auth_db.keys():
            if str(identifier) == str(auth_db[key]['key']):
                if auth_db[key]['group'] not in ['superadmin','admin','editor']:
                    return redirect('/accessdenied')
                else:
                    userid = str(key)
            else:
                return redirect('/accessdenied')
        
        date = request.form['date'].strip()
        renew_date = request.form['date-renew'].strip()
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
        pickle.dump(dict_to_store,open(filename,"wb"))
        filename = filename.replace(".db",'').replace(doccu_docs,"").replace("/","")
        return render_template('new_document_submitted.html',filename=str(filename),title=title)

@app.route("/document/new/<name>/", methods=['GET','POST'])
def document_new(name):
    if request.method == 'GET':
        if name == 'json':
            return redirect('/')
        return render_template('new_document.html',title="New Document")
    if request.method == 'POST':
        doccu_home = expanduser('~/.doccu')
        identifier = request.form['identifier']
        auth_db = pickle.load(open(doccu_home + "/ids.dbs", "rb"))

        for key in auth_db.keys():
            if str(identifier) == str(auth_db[key]['key']):
                userid = str(key)
            else:
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
        pickle.dump(dict_to_store,open(filename,"wb"))
        filename = filename.replace(".db",'').replace(doccu_docs,"").replace("/","")
        print(filename)
        return render_template('new_document_submitted.html',title=title,filename=str(filename))

if __name__ == "__main__":
    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    print("Running on port 5000, logging to error.log")
    app.run(host='0.0.0.0',debug=True)
