'''
Created on 10.10.2009

Various tools for work

@author: raidan
'''
from threading import Thread
import sys
import traceback
import httplib2
import time
from fw_patches.FwConst import TABLESPACE, KNOWN_TABLESPACES

# Reading required settings from 'settings.ini'
def readfile(filename, encoding='windows-1251'):
    '''
    Reading file and moving it into dictionary
    
    filename - existing file
    encoding - encoding of given file 
    '''
    out = dict()
    with open(filename, encoding=encoding) as settings_file:
        for line in settings_file:
            line = line.rstrip()
            if line[:1] != '#' and len(line) > 0:
                key, value = line.split('=', 1)
                out[key] = value.rstrip()
    return out

def loadfile(filename, encoding='windows-1251'):
    '''
    Загрузка содержимого файла в строку
    '''
    with open(filename, encoding=encoding) as file:
        return file.read()
    
def savefile(filename, body, encoding='windows-1251'):
    '''
    Сохранение строки в файл
    '''
    with open(filename, encoding=encoding, mode='w') as file:
        file.write(body)

def filter_ts(lines, targetTablespace):
        
    tablespaceMap = {}
    for ts in KNOWN_TABLESPACES:
        tablespaceMap[ts] = targetTablespace
    
    
    def map_ts(line, ts):
        tsline = TABLESPACE + ' ' + ts
        lineupper = line.upper()
        idx = lineupper.find(tsline)
        if idx < 0:
            return line
        replace = ''
        if ts in tablespaceMap:
            replace = TABLESPACE + ' ' + tablespaceMap[ts]
        
        line = line[:idx] + replace + line[idx + len(tsline):]   
        return line
    
    def map_ts2(line, ts):
        tsline = "'" + TABLESPACE + ':' + ts + "'"
        lineupper = line.upper()
        idx = lineupper.find(tsline)
        if idx < 0:
            return line
        replace = ''
        if ts in tablespaceMap:
            replace = "'" + tablespaceMap[ts] + "'"
        
        line = line[:idx] + replace + line[idx + len(tsline):]   
        return line
    
    
    # Отремапим табличные пространства
    targetLines = []
    for line in lines:
        for ts in KNOWN_TABLESPACES:
            line = map_ts(line, ts)
            line = map_ts2(line, ts)
        
        targetLines.append(line)
    
    
    return targetLines


class StopWatch():
    '''
    Easy classical stopwatch
    '''
    def __init__(self):
        '''
        constructor
        '''
        self.started = False
        self.startTime = 0
        self.previous_time = 0
        self.all_count = 0
        self.all_time = 0
        
    def start(self):
        self.started = True
        self.startTime = time.time()
        return self

    def stop(self):
        tm = self.time()
        self.previous_time = tm

        self.started = False
        self.startTime = 0
        
        self.all_count += 1
        self.all_time += tm
        
        return tm
    
    def restart(self):
        self.stop()
        self.start()
    
    def time(self):
        if self.started:
            return time.time() - self.startTime
        else:
            return 0
    
    def timeint(self):
        return int(self.time())
    
    def time_previous(self):
        return self.previous_time
    
    def time_previous_int(self):
        return int(self.time_previous())
    
    def total_time(self):
        return self.all_time
    def total_count(self):
        return self.all_count
    
class HttpAuthConnection():
    '''
    Http connection wrapper, automatically deal with authorization stuff
    '''
    def __init__(self, username, password, headers, print_traceback = True):
        self.http = httplib2.Http()
        self.username = username
        self.password = password
            
        if username is not None and password is not None:
            self.http.add_credentials(username, password, '')

        self.headers = headers
        self.originalHeaders = headers.copy()
        
        self.print_traceback = print_traceback       
    
    def setDefaultCall(self, url, body):
        self.default_url = url
        self.default_body = body
        
    def onFailureCommon(self):
        '''
        Common method, using on failure when executing request
            
            http -- instance of Http connection
        '''
        # Do not forget about closing
        list(self.http.connections.values()).pop().close()
        
        # We must clear headers and restore it's original values
        # To forget about session variables, of cause
        self.headers.clear()
        self.headers.update(self.originalHeaders)
        
    def proxyReturn(self, resp, content):
        '''
        Default proxy return
        '''
        return resp, content
    
    def call(self, url, body, onsuccess=None, onfailure=None, method='POST'):
        '''
        Method for calling given url
            onsuccess -- method we calling if call was success (receive status 200)
            onfailure -- method we calling if call was incorrect 
                (receive status not 200 or exception during call) 
        '''
        #print ('Connecting to server {0} as {1}'.format(url, self.username))
        
        if url is None:
            if self.default_url is not None:
                url = self.default_url
            else:
                raise BaseException('Url is none and default_url is not sets. Cannot connect')
        
        if body is None:
            if self.default_body is not None:
                body = self.default_body
            else:
                raise BaseException('Body is none and default_body is not sets. Cannot connect')
        
        if onsuccess is None:
            onsuccess = self.proxyReturn
        if onfailure is None:
            onfailure = self.proxyReturn
        
        try:
            resp, content = self.http.request(url, method, body, headers=self.headers)
        except:
            self.onFailureCommon()
            if self.print_traceback:
                traceback.print_exc()

            return onfailure(None, sys.exc_info()[1])
            
        # Set up autorization cookie
        # We must set up authorization cookie into headers
                
        # Otherwise we'll make new session on every call
        # That is deadly for Weblogic. 200 000 sessions is deadly trick.
        if self.username is not None and 'set-cookie' in resp:
            cookie = resp['set-cookie']
            value = cookie.split(';', 1)[0]
            self.headers['Cookie'] = value
            print ('Change headers after accepted cookies to ', self.headers)
                
        if resp.status == 200:
            return onsuccess(resp, content)
        else:
            self.onFailureCommon()
            return onfailure(resp, content)
        
        
        
class WatchingThread(Thread):
    def __init__(self, method):
        '''
            method -- the method we launching in separate thread
        '''
        super(WatchingThread, self).__init__()
        self.counter = 0
        self.name = 'Separate starting thread'
 
        self.method = method

    def run(self):
        if self.method:
            self.method()

