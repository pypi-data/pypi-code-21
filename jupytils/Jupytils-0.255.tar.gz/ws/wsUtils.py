from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_restful import Resource, Api
from json import dumps
import sys, os, importlib, inspect

def loadModule(config_file):
    with open(config_file) as f:
        code = compile(f.read(), config_file, 'exec')
        exec(code, globals(), locals())

def Run(file=None, method=None, reload=False):
    if (file not in sys.modules):
        im = importlib.import_module(file)
    elif(reload):
        im = importlib.reload(file)

    if (file not in sys.modules):
        return ("No File: " + file);

    im = importlib.import_module(file)

    thefunc = getattr(im, method)
    if (thefunc is None):
        return "No Method: " + method 

    return thefunc();

def default():
    ret = "Test\n\n"
    print(ret)
    return ret

cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
print(cmd_folder);

if __name__ == '__main__':
    Run('test', 'default');

