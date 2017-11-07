# coding: utf-8

import os
import re
import sys
import json
import codecs
import requests
import tools

class NuDB(object):

    def __init__(self):        
        # default host and port
        host = 'localhost'
        port = '5800'
        self.api = 'http://'+ host + ':' + port + '/nudb/'
        self.db = 'test'

    def connect(self, host, port, db):
        self.api = 'http://'+ host + ':' + port + '/nudb/'
        self.db = db

    def rput(self, data, data_type, *recBeg):
        """ data_type: json/text """
        if data == "":
            return 'Empty data.'

        url = self.api + 'rput'
        opts = {
            'db': self.db,
            'data': data,
            'format': data_type
        }

        # data type: text
        if data_type == 'text' and isinstance(data, str):
            # 檢查是否有recBeg
            if len(recBeg) == 1:
                # replace \\ -> \
                opts['data'] = re.sub('\\\\\\\\','\\\\', data)
                opts['recbeg'] = recBeg[0]
            else:
                return 'Must have recBeg.'
        elif data_type == 'json':
            # 檢查為是否為正確的JSON格式, 若正確則判斷是JSON object 或 string
            check = tools.check_JSON(data)
            if check == 1:
                # JSON object
                opts ['data'] = json.dumps(data)
            elif check < 1:
                return 'Invalid JSON format.'
        else:
            return "Wrong format. Must be 'json' or 'text'."

        res = requests.post(url, opts)
        return res
    
    def fput(self, filePath, data_type, *recBeg):
        """ data_type: json/text """
        url = self.api + "fput"
        opts = {
            'db': self.db,
            'format': data_type
        }
        fileData = {
            'file': codecs.open(filePath, 'rb', 'utf-8')
        }

        if data_type != 'text' and data_type != 'json':
            return "Wrong format. Must be 'json' or 'text'."

        if data_type == 'text':
            # 檢查是否有recBeg
            if len(recBeg) == 1:
                opts['recbeg'] = recBeg[0]
            else:
                return 'Must have recBeg.'

        res = requests.post(url, opts, files=fileData)
        return res

    def rget(self, rid):
        url = self.api + "rget"
        
        opts = {
            'db': self.db,
            'rid': rid,
            'out': 'json'
        }
        
        res = requests.get(url, opts)
        return res

    def rdel(self, rid):
        url = self.api + "rdel"
        
        opts = {
            'db': self.db,
            'rid': rid,
            'out': 'json'
        }
        
        res = requests.post(url, opts)
        return res
    
    def rupdate(self, rid, data, data_type):
        """ data_type: json/text """
        url = self.api + "rupdate"
        opts = {
            'db': self.db,
            'getrec': 'n',
            'out': 'json',
            'rid': rid,
            'format': data_type,
            'record': data
        }
        
        if rid == "" or data == "":
            return 'Must have rid and data.'

        if data_type == 'text' and isinstance(data, str):
            # replace \\ -> \
            opts['record'] = re.sub('\\\\\\\\','\\\\', data)
        elif data_type == 'json':
            #檢查是 JSON object 或 string
            check = tools.check_JSON(data)
            
            if check == 1:
                # json object
                opts['record'] = json.dumps(data)
            elif check < 1:
                return 'Invalid JSON format'
        else:            
            return "Wrong format. Must be 'json' or 'text'."

        res = requests.post(url, opts)
        return res
                
    def search(self, opts):
        url = self.api + "query"        
        res = requests.get(url, opts)
        return res