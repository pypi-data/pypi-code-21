from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_restful import Resource, Api
from json import dumps
import sys, os, importlib, inspect

def GetCustomer(dreq={}):
    req = request or dreq;
    return str(req)

def default():
    return "Test\n\n";

if __name__ == '__main__':
    default();

