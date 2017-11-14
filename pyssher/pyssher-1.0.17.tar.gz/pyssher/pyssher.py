#coding=utf-8
from __future__ import division
from __future__ import print_function
import os
import sys
import paramiko
import stat
import time
import datetime
import hashlib
import threading
import logging
import time
import functools
import re

logger = logging.getLogger('pyssher')
#logger.setLevel(logging.DEBUG)
# handler=logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.debug("debug message")


is_debug = True
def count_time(is_debug):
    def handle_func(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            rt = None
            begin = time.time()
            rt = func(*args, **kwargs)
            logger.debug( "[{0}] spend {1}s".format(func.__name__,str(time.time() - begin) ))
            return rt
        return handle_args
    return handle_func



class ssher(object):
    #user:passwd@127.0.0.1:22
    def __init__(self, host,remote_filename = None):
        logging.info("")
        self.client = None
        self.port = 22
        self.user,self.host = tuple(host.split('@'))
        self.user,self.passwd = tuple(self.user.split(':'))
        if (len(self.host.split(':')) == 2):
            self.port = int(self.host.split(':')[1])   
            self.host = self.host.split(':')[0]
        self.remote_file_size = None
        self.last_line = b''
        self.remote_filename = remote_filename
        self.sftp_client = None
        self.client = None
    def __del__(self):
        try:
            self.sftp_client.close()
        except:
            pass
        try:
            self.client.close()
        except:
            pass
            
    def connect_required(func):
        @functools.wraps(func)
        def handle_func(*args, **kwargs):
            self = args[0]
            if (not self.client):
                self.connect()
            rt = func(*args, **kwargs)
            return rt
        return handle_func

    @count_time(is_debug)
    def connect(self):
        logger.debug("connnecting to host:{0},port:{1},user:{2}".format(self.host,self.port,self.user))
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp_client = None        
        self.client.connect(self.host,self.port,self.user,self.passwd)
        self.sftp_client = self.client.open_sftp() #paramiko.SFTPClient.from_transport(self.client.get_transport())
        return self.client

    def close(self):
        if (self.sftp_client != None):
            self.sftp_client.close()
            self.sftp_client = None
        if (self.client != None):
            self.client.close()
            self.client = None        

    @connect_required
    def exist(self,remote_path):
        try:          
            return stat.S_ISDIR(self.sftp_client.lstat(remote_path).st_mode) 
        except IOError:
            return False
    def mkdir(self,remote_path):
        try:
            return self.sftp_client.mkdir(remote_path)
        except:
            return False
    def mkdirs(self,remote_path):
        r = remote_path.split('/')
        for i in range(2,len(r) + 1):
            if self.exist('/'.join(r[0:i])) == False:
                self.mkdir('/'.join(r[0:i]))
    
    @count_time(is_debug)
    @connect_required
    def shell(self,cmd,fnout):
        chan = self.client.get_transport().open_channel(kind='session')
        logger.debug('[{0}] :{1}'.format(ssher.shell.__name__,cmd))
        chan.get_pty()  
        chan.exec_command(cmd)

        buff_size = 1024
        stdout = b""
        stderr = b""
        while not chan.exit_status_ready():
            if chan.recv_ready():
                t = chan.recv(buff_size)
                stdout += t
                if (fnout != None):
                    print(t, end="")
            if chan.recv_stderr_ready():
                t = chan.recv_stderr(buff_size)
                if (fnout != None):
                    print(t, end="")
                stderr += t
            time.sleep(0.1)
        retcode = chan.recv_exit_status()
        while chan.recv_ready():
            t = chan.recv(buff_size)
            if (fnout != None):
                print(t, end="")
            stdout += t
        while chan.recv_stderr_ready():
            t = chan.recv_stderr(buff_size)
            if (fnout != None):
                print(t, end="")
            stderr += t

        chan.close()
        return retcode, stdout, stderr

    @count_time(is_debug)
    @connect_required
    def shell2(self,cmd,fnout):
        chan = self.client.get_transport().open_channel(kind='session')
        logger.debug('[{0}] :{1}'.format(ssher.shell2.__name__,cmd))
        chan.get_pty()  
        chan.exec_command(cmd)

        buff_size = 1024
        stdout = b""
        stderr = b""
        while not chan.exit_status_ready():
            if chan.recv_ready():
                t = chan.recv(buff_size)
                stdout += t
                if (fnout != None):
                    print(t, end="")
                yield (0,t)
            if chan.recv_stderr_ready():
                t = chan.recv_stderr(buff_size)
                if (fnout != None):
                    print(t, end="")
                stderr += t
                yield (0,t)
            time.sleep(0.1)
        retcode = chan.recv_exit_status()
        while chan.recv_ready():
            t = chan.recv(buff_size)
            if (fnout != None):
                print(t, end="")
            stdout += t
            yield (0,t)
        while chan.recv_stderr_ready():
            t = chan.recv_stderr(buff_size)
            if (fnout != None):
                print(t, end="")
            stderr += t
            yield (0,t)

        chan.close()
        yield (1,retcode)

    @count_time(is_debug)
    @connect_required
    #[(local ,remote)]
    def sendfiles(self,sendfiles,check = False):
        def callback2(size, file_size):
            pass       
        bakcup = None
        nw = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        for (local,remote) in sendfiles:
            if self.exist(os.path.dirname(remote)) == False:
                self.mkdirs(os.path.dirname(remote))
            if bakcup != None and self.exist(os.path.dirname(bakcup)) == False:
                self.mkdirs(os.path.dirname(bakcup))
            if (bakcup != None):
                self.shell('sudo cp {0} {1}_{2}'.format(remote,bakcup,nw),None)
            logger.info('sftp :{0}'.format(remote))
            self.sftp_client.put(local,remote,callback=callback2)
            sys.stdout.flush()
            if (check == True):
                l_md5 = self.local_md5sum(local)
                r_md5 = self.remote_md5sum(ssh,remote)
                if (l_md5 != r_md5):
                    logger.info('sftp {3} fail:local:{0},remote:{1}'.format(l_md5,r_md5,v))                

        
    def local_md5sum(self,filename):     
        fd = open(filename,"rb")  
        fcont = fd.read()  
        fd.close()           
        fmd5 = hashlib.md5(fcont)  
        return fmd5.hexdigest()

    def remote_md5sum(self,filename):
        retcode, stdout, stderr = self.shell('md5sum {0}'.format(filename),None)
        if (retcode == 0):
            return stdout.decode('utf-8').split("  ")[0]
        else:
            print(retcode, stdout, stderr)
            return None

    def listdir(self,folder,extensions):
        ls = os.listdir(folder)
        #os.path.isfile(folder + "/" + x)
        if extensions:
            return [x for x in ls if  os.path.splitext(x)[1][1:] in extensions]
        else:
            return ls

    def listdir2(self,folder):
        dirname = os.path.dirname(folder)
        basename = os.path.basename(folder)
        ls = os.listdir(dirname)
        if extensions:
            return [x for x in ls if  os.path.splitext(x)[1][1:] in extensions]
        else:
            return ls   
    
    @count_time(is_debug)
    @connect_required
    def cat(self,path,yd = True):
        fstat = self.sftp_client.stat(path)
        remote_file = self.sftp_client.open(path, 'r')
        sz = fstat.st_size
        last_line = b''
        rt = ''
        while sz > 0:
            last_line = last_line + remote_file.read(1024)
            sz = sz - 1024
            line = ''
            try:
                line = last_line.decode()
            except Exception as e:
                print(e)
            last_line = b''
            if (yd):
                yield line
            else:
                rt = rt + line
        remote_file.close()
        #if (yd == False):
        #    return rt
        
    @count_time(is_debug)
    @connect_required
    def tail(self,path = None):
        if (path != self.remote_filename):
            self.remote_filename = path
            self.remote_file_size = None
            self.last_line = b''

        fstat = self.sftp_client.stat(self.remote_filename)
        if self.remote_file_size is None or self.remote_file_size > fstat.st_size:
            self.remote_file_size = fstat.st_size - 5000
            if (self.remote_file_size < 0):
                self.remote_file_size = 0            
        if self.remote_file_size < fstat.st_size:
            remote_file = self.sftp_client.open(self.remote_filename, 'r')
            remote_file.seek(self.remote_file_size, 0)
            sz = remote_file.stat().st_size - self.remote_file_size
            self.remote_file_size = remote_file.stat().st_size
            while sz > 0:
                self.last_line = self.last_line + remote_file.read(1024)
                sz = sz - 1024
                line = ''
                try:
                    line = self.last_line.decode()
                except Exception as e:
                    print(e)
                self.last_line = b''
                yield line
                
            remote_file.close()

    def fuzzyfinder(self,user_input, collection):
        suggestions = []
        for v in collection:
        	regex = re.compile(v.replace('.','\.').replace('*','.*'))
        	if regex.search(user_input):
        		return True
        return False

    @count_time(is_debug)
    @connect_required
    def syn(self,local_path,remote_path,include = None,exclude = None,prev_act = None,post_act = None):
        excludes = None
        if (exclude):
            excludes = exclude.strip().split(',')
        includes = None
        if (include):
            includes = include.strip().split(',')
        if (prev_act):
            self.shell(prev_act,'print')

        self.mkdirs(remote_path)
        list_files = []
        for root,dirs,files in os.walk(local_path):
            for d in dirs:
                temp = remote_path + os.path.join(root,d).replace(local_path,'')
                self.mkdirs(temp)
            for f in files:
                local = os.path.join(root,f)
                remote = remote_path + local.replace(local_path,'').replace('\\','/')
                flag = False
                if (includes == None):
                    flag = True
                else:
                    if (self.fuzzyfinder(local,includes) == True):
                        flag = True
                if (flag == True and excludes != None):
                    if (self.fuzzyfinder(local,excludes) == True):
                        flag = False
                if (flag == True):                         
                    l_m5 = self.local_md5sum(local)
                    r_m5 = self.remote_md5sum(remote)
                    #logger.debug("{0}---{1}".format(l_m5,r_m5))
                    if (l_m5 != r_m5):
                        list_files.append((local,remote))

        self.sendfiles(list_files)
        if (post_act):
            for i,k in self.shell2(post_act,None):
                logger.debug(k)
        
        
#logger.setLevel(logging.INFO)
#h = ssher('root:pomelo7788@115.159.160.101:22')
#h.syn('/Users/lxh/Documents/work/script/public/pyssher','/root/tmp',None,'*.DS_Store,*.pyc,*/dist/*','ls /root/','ls /root/')
