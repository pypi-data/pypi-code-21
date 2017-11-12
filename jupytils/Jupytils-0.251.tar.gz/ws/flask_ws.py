#!/usr/local/bin/python

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_restful import Resource, Api
from json import dumps
import sys, os, importlib, inspect
import wsUtils
import cgi

PyUtilsPATH="../../PyUtils";
sys.path.append(PyUtilsPATH)
CWD=os.getcwd()
ABS_PATH = os.path.abspath(CWD)
sys.path.append(ABS_PATH)

app = Flask(__name__)

def echo():
    tags = [t+"="+request.args[t] for t in request.args ];
    reqs =  str(request.json)
    t = str(tags)  + "\n" + reqs + "\n"
    #print (t)
    return t

def process():
    method = request.args['m'] if 'm' in request.args else 'echo' ;
    ret = ""
    print("Processing method: ", method, CWD, ABS_PATH)
    if (method.find(".") > 0):
        [mod, meth] = method.split('.')
        ret = ("Module:  {}, Method: {}\n".format(mod, meth) )
        try:
            ret = wsUtils.Run(mod, meth);
        except Exception as e:
            ret = "Error " + str(e)
    else:
        if (method != "process" and method in globals()):
            ret = globals()[method]()
        else:
            ret = "Something wrong with method: " + method + "\n"
    return ret;
#--------------------------------------------------------------------------
@app.route('/ws', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
def ws():
#    for a in request.args: print(a, request.args[a])
    if (len(request.args) <= 0):
        return "Version 1.0\n";
    r = process();
    #print(r)
    return r;

#--------------------------------------------------------------------------
@app.route('/run', methods=['POST', 'GET', 'OPTIONS', 'HEAD'])
def run():
    ret = wsUtils.Run('test', 'GetCustomer');
    return ret;

#--------------------------------------------------------------------------
'''
Help:

flask_ws port
'''
def start():
    port = 8080 if len(sys.argv) < 2 else sys.argv[1]
    print( "Starting at port: ", port)
    app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == '__main__':
    start();
