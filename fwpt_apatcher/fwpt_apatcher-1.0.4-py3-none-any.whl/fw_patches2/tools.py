'''
Created on 10.10.2009

Various tools for work

@author: raidan
'''
from fw_patches2 import Const
from fw_patches2.Const import SVN_UPDATE, DYNAMIC_START, DBOPTION_PARTITIONING, \
    KNOWN_DBOPTIONS, TABLESPACE, TABLESPACE_NORMAL, KNOWN_TABLESPACES
from threading import Thread
import imp
import os
import pickle
import string
import subprocess
import sys
import time
import traceback

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


def loadfile_bin(filename):
    '''
    Загрузка бинарных данных из файла
    '''
    with open(filename, mode='rb') as file:
        return pickle.load(file)
    
def savefile_bin(filename, body):
    '''
    Сохранение бинарных данных в файл
    '''
    with open(filename, mode='wb') as file:
        pickle.dump(body, file)

def safe_filename(filename):
    '''
    Обезопасим название
    '''
    
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    def check(c):
        if c in valid_chars:
            return c
        else:
            return '_'
    
    return ''.join(check(c) for c in filename)


def import_python_lib(filename):
    """ 
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do. 
    """
    path, filename = os.path.split(os.path.realpath(filename))
    filename = os.path.splitext(filename)[0]
    print ('Searching module [{0}] in [{1}]'.format(filename, path))
    sys.path.append(path)
    module = __import__(filename)
    imp.reload(module)
    del sys.path[-1]
    print ('Successfully included module', filename)
    return module


def update_svn(patchesDir):
    '''
    Обновление указанного каталога с помощью Subversion
    '''
    print ('Updating subversion directory [{0}]...'.format(patchesDir))
    proc = subprocess.Popen(SVN_UPDATE.format(patchesDir), shell=True, bufsize=10000,
                            stdin=None, stdout=sys.stdout, stderr=sys.stderr)
    ret = proc.wait()
    if ret != 0:
        print ('Maybe you don''t have Subversion?')
    
    print ('Successfully updated subversion dir')

def _arg_option(name):
    '''
    Извлечение опции из системных аргументов
    '''
    if name in sys.argv:
        sys.argv.remove(name)
        print ('Using option', name)
        return True
    return False

def _arg_option_value(name):
    '''
    Извлечение опции из системных аргументов
    '''
    if name in sys.argv:
        return sys.argv.remove(name)
    return None


def _extract_option(config, name):
    tempConfig = config.split("\n")
    found = None
    for c in tempConfig:
        if c[:len(name)] == name:
            found = c[len(name):]
            if found[:1] == '=':
                found = found[1:]
            else:
                found = True
            tempConfig.remove(c)
                       
            
    config = '\n'.join(tempConfig)
    return config, found 

def _getch():
    '''
    Просьба нажать клавишу на клавиатуре.
    Реализация зависит от используемой ОС (поддерживаем Windows и *nix)
    '''
    print('Press any key to continue...')
    try:
        # Win32
        from msvcrt import getch
        getch()
    except ImportError:
        # UNIX
        def getch():
            # Ignore non existing termios on Windows
            import sys, tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                return sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

        getch()


def basic_filter(lines, dbOptions, tablespaceMap):
    # Условия по опциям БД
    
    if dbOptions is None:
        dbOptions = []
        
    if tablespaceMap is None:
        tablespaceMap = {}
    
    targetLines = [] 
    accept = True
    processing = False
    for line in lines:
        linestrip = line.strip()
        if linestrip == Const.DYNAMIC_END:
            if processing:
                processing = False
            else:
                targetLines.append(line)
            accept = True
        elif linestrip.startswith(DYNAMIC_START):
            condition = line[len(DYNAMIC_START):]
            if condition in KNOWN_DBOPTIONS:
                processing = True            
                if condition.strip() in dbOptions:
                    print (' ACCEPTED DB OPTION', condition)
                    accept = True
                else:
                    print (' INACCEPTED DB OPTION', condition)
                    targetLines.append('')
                    targetLines.append('-- SKIPPED DB OPTION ' + condition)
                    accept = False
            else:
                targetLines.append(line)
        else:
            if accept:
                targetLines.append(line)
    
    # Известные нам опции БД
    
    accept = True
    lines = targetLines
    targetLines = []
    for line in lines:
        linestrip = line.strip()
        if linestrip.endswith(';'):
            if not accept:
                targetLines.append(';')
            else:
                targetLines.append(line)
            accept = True
        elif linestrip.upper().startswith('PARTITION BY'):
            if not DBOPTION_PARTITIONING in dbOptions:
                print (' INACCEPTED PARTITION OPTION', DBOPTION_PARTITIONING)
                targetLines.append('-- SKIPPED ' + DBOPTION_PARTITIONING)
                accept = False
            else:
                print (' ACCEPTED PARTITION OPTION', DBOPTION_PARTITIONING)
                accept = True
                targetLines.append(line)
        else:
            if accept:
                targetLines.append(line)
    
    
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
    
    def map_ts3(line, ts):
        tsline = "STORE IN ("+ ts +")"
        lineupper = line.upper()
        idx = lineupper.find(tsline)
        if idx < 0:
            return line
        replace = ''
        if ts in tablespaceMap:
            replace = "STORE IN ("+ tablespaceMap[ts] +")"
        
        line = line[:idx] + replace + line[idx + len(tsline):]   
        return line
    
    
    # Отремапим табличные пространства
    lines = targetLines
    targetLines = []
    
    expectedTablespaceMap = []
    expectedTablespaceMap.extend(KNOWN_TABLESPACES)
    expectedTablespaceMap.extend(tablespaceMap.keys())
    
    
    for line in lines:
        for ts in expectedTablespaceMap:
            line = map_ts(line, ts)
            line = map_ts2(line, ts)
            line = map_ts3(line, ts)
        
        targetLines.append(line)
    
    
    return targetLines
    

def check_ui(ui):
    if _arg_option('--noui'):
        return False
    return ui
    

def execute(func, ui = False):
    '''
    Выполнение переданной функции с отслеживанием этого выполнения.
    Если работаем в режиме ui, то в случае ошибки просим подтвердить нажатием клавиши,
    что данная ошибка прочитана
    '''

    ui = _arg_option('--ui') or ui
    allOK = False
    
    watch = StopWatch()    
    watch.start()
    try:
        func()
        allOK = True
        if ui:
            print ('ALL OK')
    except:
        if ui and not allOK:
            traceback.print_exc()
            print ('\n----------------------------- ')
            print ('Error when preparing patches...')
            _getch()
            sys.exit(1)
        else:
            raise
    finally:
        time = watch.stop()
        sys.stdout.write('\nTIME: {0:.2f} sec\n'.format(time))


def print_last_errors(logName, stdout):
    if logName is not None and logName != '':
        f = open(logName, 'r')
        last_lines = ">>> ".join(f.readlines()[-15:])
        f.close()
        stdout.write('\n\nLast 15 lines:')
        stdout.write(last_lines)
        stdout.write('\n')

# Our new exception
class PatchException(BaseException):
    pass


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

