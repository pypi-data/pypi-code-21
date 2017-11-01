# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""
import os
import sys
import importlib

def get_package_folder(name):
    package = importlib.import_module('name')
    dirname,filename = os.split(package.__file__)
    return dirname

def fix(*args,**kwargs):
    return os.path.normpath(os.path.join(*args,**kwargs))
    
def include_entire_directory(source_dir,dest_dir):
    m = len(source_dir)
    include = [(source_dir, dest_dir)]
    for root, subfolders, files in os.walk(source_dir):
        for filename in files:
            source = fix(root, filename)
            dest = fix(dest_dir, root[m+1:], filename)
            include.append((source,dest))
    return include

def find_script_path():
    if getattr(sys, 'frozen', False):
        script_path= os.path.dirname(sys.executable)
    else:
        script_path = os.path.dirname(__file__)

    return script_path

python_installed_directory = os.path.dirname(sys.executable)

def abs_user_path():
    return os.path.abspath(os.path.normpath(os.path.expanduser('~')))

def build_windows_uuid():
    import uuid
    uuid = '{'+str(uuid.uuid4())+'}'
    return uuid
