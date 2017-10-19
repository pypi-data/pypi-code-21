#!/usr/bin/env python
"""
"""
import os
import codecs
import json


import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from markdown.extensions.toc import TocExtension
from mdx_gfm import GithubFlavoredMarkdownExtension as GFMExt
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = '6ppCa7=i)GXLjbhwNQ)U3z#7' # Change this in production

if os.path.exists('smeagol.json'):
    with open('smeagol.json') as f:
        cfg = json.loads(f.read())
else:
    cfg = {'name': 'smeagol', 'title': 'smeagol | a python wiki'}


def run():
    app.run()


@app.route('/')
def home():
    """Displays the home page of the wiki."""
    pages = ['home.md', 'Home.md']

    # Search for the home page. If found, render the home page.
    files = [ f for f in os.listdir('.') if f.endswith('.md') ]
    for page in pages:
        if page in files:
            path = '/page/{}'.format(page.replace('.md', ''))
            return redirect(path)
    
    # Handle page not found
    content = 'No home page created. You should create one.'
    return render_template('page.html', content=content, conf=cfg)


@app.route('/pages')
def show_all_pages():
    """Shows a list of all pages."""
    wiki_pages = []

    # Create the full list of pages
    for path, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.md'):
                url_path = '/'.join(path.split(os.sep))
                full_path = '/'.join([url_path, f.replace('.md', '')])
                if full_path.startswith('./'):
                    full_path = full_path.replace('./', '')
                wiki_pages.append(full_path)

    # Render the list as HTML
    html = ''
    for page in wiki_pages:
        href = '/page/{}'.format(page)
        link = '<a href="{}">{}</a>'.format(href, page)
        html += '<h5>{}</h5>'.format(link)
    cfg['page_name'] = ''
    return render_template('page.html', content=html, conf=cfg)


@app.route('/page/<path:page>')
def show_page(page):
    """Renders the requested page."""
    page = '{}.md'.format(page)

    # Handle page not found
    if not os.path.isfile(page):
        content = 'No home page created. You should create one.'
        return render_template('page.html', content=content, conf=cfg)
    
    # Render the page
    with codecs.open(page, mode='r', encoding='utf-8') as f:
        text = f.read()
    content = markdown.markdown(text, extensions=[
                                                GFMExt(),
                                                WikiLinkExtension(base_url='/page/', 
                                                                  end_url=''),
                                                TocExtension()])
    cfg['page_name'] = page.replace('.md', '')
    return render_template('page.html', content=content, conf=cfg)


@app.route('/page/create', methods=['GET', 'POST'])
def create_page():
    """Create a page"""
    if request.method == 'GET':
        cfg['page_name'] = ''
        cfg['page_title'] = 'Create Page'
        cfg['has_error'] = ''
        cfg['page_action'] = '/page/create'
        cfg['input_type'] = 'text'
        cfg['disabled'] = ''
        cfg['has_error'] = ''
        return render_template('editor.html', markdown='', conf=cfg)
    elif request.method == 'POST':
        try:
            page_id = request.form['page_id']
            page_md = request.form['markdown']
        except:
            return 'A form error occured. Could not create page.', 500

        # Check if file exists already, if so panic
        page_file = '{}.md'.format(page_id)
        if os.path.isfile(page_file):
            cfg['has_error'] = 'has-error'
            flash('Page already exists')
            return redirect('/page/create')

        # Write to file
        with open(page_file, 'w') as f:
            f.write(page_md)

        path = '/page/{}'.format(page_id)
        return redirect(path)

    


@app.route('/page/edit/<path:page>', methods=['GET'])
def edit_page_get(page):
    """Edit a page"""
    page = '{}.md'.format(page)

    # Handle page not found
    if not os.path.isfile(page):
        content = 'Page does not exist. Nothing to edit.'
        return render_template('layout.html', content=content, conf=cfg)
    
    # Render the page
    with codecs.open(page, mode='r', encoding='utf-8') as f:
        text = f.read()
    cfg['page_name'] = page.replace('.md', '')
    cfg['page_name_val'] = page.replace('.md', '')
    cfg['page_title'] = 'Edit {}'.format(page.replace('.md', ''))
    cfg['page_action'] = '/page/edit/{}'.format(page.replace('.md', ''))
    cfg['disabled'] = ''
    cfg['input_type'] = 'hidden'
    cfg['has_error'] = ''
    return render_template('editor.html', markdown=text, conf=cfg)


@app.route('/page/edit/<path:page>', methods=['POST'])
def edit_page_post(page):
    try:
        page_id = request.form['page_id']
        page_md = request.form['markdown']
    except:
        print page_id
        print page_md
        return 'A form error occured. Invalid data.', 500

    page_file = '{}.md'.format(page_id)

    # Handle file not found
    if not os.path.isfile(page_file):
        return 'A form error occured. File Not found.', 500

    # Write to file
    with open(page_file, 'w') as f:
        f.write(page_md)

    new_path ='/page/{}'.format(page)
    return redirect(new_path, code=302)
    #return render_template('page.html', content=content, conf=cfg)


@app.route('/page/delete/<path:page>')
def delete_page(page):
    return render_template('page.html', content='Delete not implemented yet', conf=cfg)


if __name__ == '__main__':
    app.run()


