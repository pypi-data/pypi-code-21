#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import subprocess
import codecs
import shlex
import socket

from flask import Blueprint, send_from_directory, request, abort, Response, current_app
MONO_REPOS = 0
MULTI_REPOS = 1

from functools import wraps
def check_repo():
    def decorator(func):
        @wraps(func)
        def onCall(*args, **kw):
            if kw['repo'] != '1964dffg5fdg52kjiff': #for index multi_repos
                repo_root = os.path.join(current_app.config['REPO_ROOT'], '%s.git' % kw['repo'])
                if not os.path.isdir(repo_root):
                    repo_root = os.path.join(current_app.config['REPO_ROOT'], kw['repo'])
                    if not os.path.isdir(repo_root):
                        abort(404)
                kw['repo'] = repo_root    
            return func(*args, **kw)
        return onCall
    return decorator

INDEX_MULTI_REPOS = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Git WebUI</title>
        <link rel="stylesheet" type="text/css" href="./1964dffg5fdg52kjiff/css/bootstrap.css">
        <link rel="stylesheet" type="text/css" href="./1964dffg5fdg52kjiff/css/git-webui.css">
        <link rel="icon" href="./1964dffg5fdg52kjiff/img/git-icon.png" />
    </head>
    <body>
        <script src="./1964dffg5fdg52kjiff/js/jquery.min.js"></script>
        <script src="./1964dffg5fdg52kjiff/js/bootstrap.min.js"></script>
        <div id="global-container">
            <div id="sidebar">
                <a href="."><img id="sidebar-logo" src="./1964dffg5fdg52kjiff/img/git-logo.png"></a>
                <div id="sidebar-content">
                    <section id="sidebar-repos"><h4>Repository</h4>
                        <ul>
                            %s
                        </ul>
                    </section>
                </div>
            </div>
        </div>
    </body>
</html>
"""

def process(cmd, stdin, add_footers, repo_root, env = None):
    git = subprocess.Popen(cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = repo_root, env = env)
    stdout, stderr = git.communicate(stdin)
    if add_footers:
        stdout = stdout + stderr
        stdout = stdout + b"\r\n"
        stdout = stdout + codecs.encode("\r\nGit-Stderr-Length: " + str(len(stderr)), "utf-8")
        stdout = stdout + codecs.encode("\r\nGit-Return-Code: " + str(git.returncode), "utf-8")
    elif git.returncode != 0:
        print(stderr)
    return stdout

def indexrepo():
    reposs = ""
    for repo in os.listdir(current_app.config['REPO_ROOT']):
        if repo[-4:] == '.git':
            repo = repo[:-4]
        reposs = reposs + '<li title="%s"><a href="./%s">%s</a></li>' % (repo,repo, repo)
    return INDEX_MULTI_REPOS % reposs

def index(repo=None):
    return static_web('index.html')

def static_web(path, repo=None):
    return send_from_directory(current_app.config['WEB_ROOT'],path)

def catfile(path, repo=None):
    repo_root = current_app.config['REPO_ROOT']
    if repo:
        repo_root = repo
    r = Response(response=process(["git", "-c", "color.ui=false", "cat-file", "-p", path], b"", False, repo_root), status=200, mimetype="text")
    r.headers["Content-Type"] = ""
    return r

def urlrepos(repo=None):
    #return codecs.encode(socket.gethostname(), "utf-8")
    if repo and repo[-4:] == '.git':
        return os.getenv('GITWEBUI_URL', request.url[:-9]+'.git')   
    return os.getenv('GITWEBUI_URL', request.url[:-9])   

def dirname(repo=None): 
    repo_root = current_app.config['REPO_ROOT']
    if repo:
        repo_root = repo
    wc = os.path.split(repo_root)[1]
    return codecs.encode(wc, "utf-8")

def viewonlytrue(repo=None): 
    return "1"

def viewonlyfalse(repo=None): 
    return "0"

def urlindexmultirepos(repo=None): 
    return "../."

def urlindexmonorepos(repo=None): 
    return "."

def git(repo=None):
    repo_root = current_app.config['REPO_ROOT']
    if repo:
        repo_root = repo
    content =""
    for key in request.form.to_dict():
        if len(content):
            content = content + "&"
        if len(request.form.to_dict()[key]):
            content = key + "=" + request.form.to_dict()[key]
        else:
            content = key
    # Convention : First line = git arguments, rest = git process stdin
    i = content.find('\n')
    if i != -1:
        args = content[:i]
        stdin = content[i + 1:]
    else:
        args = content
        stdin = b""
    cmd = shlex.split("git -c color.ui=true " + args)
    return  process(cmd, stdin, True, repo_root)

class BlueGitWebUi(Blueprint):

    def __init__(self, name='gitwebui', import_name=__name__, url_prefix="", mode=MULTI_REPOS, viewonly=True, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, url_prefix, *args, **kwargs)
        self._add_url_rule(mode, viewonly)
        self.before_app_first_request(self._add_web_root)
        if mode == MULTI_REPOS:
            self.before_app_first_request(self._check_repo)
        
    def _add_url_rule(self, mode, viewonly):
        if mode == MONO_REPOS:
            self.add_url_rule('/', 'index', index, methods=['GET'])
            self.add_url_rule('/<path:path>', 'static_web', static_web, methods=['GET'])
            self.add_url_rule('/git/cat-file/<path:path>', 'catfile', catfile, methods=['GET'])
            self.add_url_rule('/dirname', 'dirname', dirname, methods=['GET'])
            self.add_url_rule('/urlrepos', 'urlrepos', urlrepos, methods=['GET'])
            if viewonly:
                self.add_url_rule('/viewonly', 'viewonly', viewonlytrue, methods=['GET'])
            else:
                self.add_url_rule('/viewonly', 'viewonly', viewonlyfalse, methods=['GET'])
            self.add_url_rule('/git', 'git', git, methods=['POST'])
            self.add_url_rule('/urlindex', 'urlindex', urlindexmonorepos, methods=['GET'])
        if mode == MULTI_REPOS:
            self.add_url_rule('/', 'indexrepo', indexrepo, methods=['GET'])
            self.add_url_rule('/<repo>/', 'index', index, methods=['GET'])
            self.add_url_rule('/<repo>/<path:path>', 'static_web', static_web, methods=['GET'])
            self.add_url_rule('/<repo>/git/cat-file/<path:path>', 'catfile', catfile, methods=['GET'])
            self.add_url_rule('/<repo>/urlrepos', 'urlrepos', urlrepos, methods=['GET'])
            self.add_url_rule('/<repo>/dirname', 'dirname', dirname, methods=['GET'])
            if viewonly:
                self.add_url_rule('/<repo>/viewonly', 'viewonly', viewonlytrue, methods=['GET'])
            else:
                self.add_url_rule('/<repo>/viewonly', 'viewonly', viewonlyfalse, methods=['GET'])
            self.add_url_rule('/<repo>/git', 'git', git, methods=['POST'])
            self.add_url_rule('/<repo>/urlindex', 'urlindex', urlindexmultirepos, methods=['GET'])
    
    def _add_web_root(self):
        current_app.config['WEB_ROOT'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        if sys.version <= '3':
            current_app.config['WEB_ROOT'] = os.path.join(os.path.dirname(os.path.abspath(__file__)).decode('utf-8'), 'static')
        
    def _check_repo(self):
        for endpoint in ['index', 'static_web', 'catfile', 'urlrepos', 'dirname', 'viewonly', 'git', 'urlindex']:
            current_app.view_functions['%s.%s' % (self.name, endpoint)] = check_repo()(current_app.view_functions['%s.%s' % (self.name, endpoint)])