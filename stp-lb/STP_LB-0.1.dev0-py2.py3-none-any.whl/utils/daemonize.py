#!/usr/bin/env python
#coding: utf-8
import sys
import os
import time


def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'): 
    try:  
        pid = os.fork()  
        if pid > 0: 
            sys.exit(0) 
    except OSError as e:  
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) ) 
        sys.exit(1) 
 
  #os.chdir("/")
    os.chdir(os.getcwd())
    os.umask(0)
    os.setsid()
 
    try:  
        pid = os.fork()  
        if pid > 0: 
            sys.exit(0) 
    except OSError as e:  
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) ) 
        sys.exit(1) 
 
    for f in sys.stdout, sys.stderr: f.flush() 
    si = open(stdin, 'r') 
    so = open(stdout, 'a+') 
    se = open(stderr, 'a+', 0) 
    os.dup2(si.fileno(), sys.stdin.fileno()) 
    os.dup2(so.fileno(), sys.stdout.fileno()) 
    os.dup2(se.fileno(), sys.stderr.fileno()) 

def main():   
    import time   
    sys.stdout.write('Daemon started with pid %d\n' % os.getpid())   
    sys.stdout.write('Daemon stdout output\n')   
    sys.stderr.write('Daemon stderr output\n')   
    c = 0   
    while True:   
        sys.stdout.write('%d: %s\n' %(c, time.ctime()))   
        sys.stdout.flush()   
        c = c+1   
        time.sleep(1)   

def test_signal():
    import signal
    import os
    def handler(signum, frame):
        print('-----------')
        print(signum)
        print('-----------')
        exit()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(15)
    while True:
        print("running")
        time.sleep(1)

   
if __name__ == "__main__":   
    print("ok1")
    daemonize('/dev/null','daemon_stdout.log','daemon_error.log')   
    print('ok2')
    #main()   
    test_signal()
