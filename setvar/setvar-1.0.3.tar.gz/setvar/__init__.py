# Here we define some utility commands to simplify interaction with the shell.
# You don't need to read or understand this, but it's here in case you want to.
from subprocess import *
import re
import os
import pickle

variables_set = {}
variables_hide = {}
variable_set_time = 0
variable_set_file = "env.dat"

def loadvar():
    repvar("")
    for k in variables_set:
        v = variables_set[k]
        if k in variables_hide:
            print(k+"=.....")
        else:
            print(k+"="+v)
def hidevar(k):
    global variables_set, variable_set_time, variable_set_file, variables_hide
    variables_hide[k]=1
def repvar(v):
    """
    repvar() is short for "Replace Variables." The idea is that this
    function looks for strings of the form $VAR or ${VAR} or even
    $(CMD) in the input string and replaces them, either with
    the contents of os.environ[VAR] or os.pipe(CMD), mimicking the
    behavior of bash. If a backslace precedes the $, then the backslash
    will be removed but the string will not be evaluated. Thus:
    ${HOME} becomes "/home/user"
    $HOME becomes "/home/usr"
    $(echo Hello) becomes "Hello"
    \$HOME becomes $HOME
    """
    global variables_set, variable_set_time, variable_set_file, variables_hide
    if os.path.exists(variable_set_file) and os.path.getmtime(variable_set_file) > variable_set_time:
        fd = open(variable_set_file,"rb")
        try:
          variables_set = pickle.load(fd)
        except:
          variables_set = {}
        try:
          variables_hide = pickle.load(fd)
        except:
          variables_hide = {}
        fd.close()
        for k in variables_set:
            os.environ[k] = variables_set[k]
    epos = 0
    buf = ''
    v = str(v)
    for g in re.finditer(r'\$((\w+)|\{([^}]*)\}|\(([^())]*)\))|(\\+\$)',v):
        if g:
            i = 2
            while g.group(i) == None:
                i += 1
            p = g.start(0)
            buf += v[epos:p]
            epos = p + len(g.group(0))
            if i == 4:
                #fh = os.popen(g.group(i),"r")
                fh = Popen(g.group(i),shell=True,close_fds=True,stdout=PIPE,stderr=STDOUT).stdout
                c = repvar(fh.read().decode('utf-8'))
                fh.close()
            elif i == 5:
                c = '$'
            else:
                if not g.group(i) in os.environ:
                    raise Exception("no such environment variable: "+g.group(i))
                c = repvar(os.environ[g.group(i)])
            buf += c
        else:
            break
    buf += v[epos:]
    return buf.strip()
def setvar(e):
    """
    setvar() emulates the ability of BASH to set environment variables.
    Thus, NAME=VALUE will set os.environ["NAME"]="VALUE". Bash-style
    comments will be stripped, and bash-line continuations will be processed.
    """
    global variables_set, variable_set_time, variable_set_file, variables_hide
    mod = False
    e = re.sub(r'#[^\r\n]*','',e)
    e = re.sub(r'\\\n\s*','',e)
    for m in re.finditer(r'(?m)(\w+)=(.*)',e):
        k = m.group(1)
        v = repvar(m.group(2))
        if k in variables_hide:
            print(k+"=.....")
        else:
            print(k+"="+v)
        if k in variables_set and v == variables_set[k]:
            pass
        else:
            os.environ[k]=v
            mod = True
            variables_set[k]=v
    if mod:
        storevar()
def storevar():
    # Make sure the file has the right permissions
    fd = os.open(variable_set_file,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    os.close(fd)
    fd = open(variable_set_file,"wb")
    pickle.dump(variables_set, fd)
    pickle.dump(variables_hide, fd)
    fd.close()
    variable_set_time = os.path.getmtime(variable_set_file)
def readfile(f):
    """
    Reads in a file. repvar() will be applied to the file name.
    """
    n = repvar(f)
    print("Reading file `"+n+"'")
    fh = open(n)
    c = fh.read()
    fh.close()
    return c
def writefile(f,c):
    """
    Writes out a file. repvar() will be applied both to the file name
    and the file contents.
    """
    c = str(c)
    n = repvar(f)
    print("Writing file `"+n+"'")
    fd = os.open(n.encode('utf-8'),os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    os.write(fd,repvar(c).encode('utf-8'))
    os.close(fd)
    #fh = open(n,"w")
    #fh.write(repvar(c))
    #fh.close()

import getpass
def readpass(n):
    global variables_set, variable_set_time, variable_set_file, variables_hide
    print("Password or secret: "+n)
    f = n+".txt"
    if os.path.exists(f):
        os.environ[n] = readfile(f)
    else:
        os.environ[n] = getpass.getpass()
        writefile(f,"$"+n)
    variables_set[n] = os.environ[n]
    variables_hide[n] = 1
    storevar()
