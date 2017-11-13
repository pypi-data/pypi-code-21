# Here we define some utility commands to simplify interaction with the shell.
# You don't need to read or understand this, but it's here in case you want to.
from subprocess import *
import re
import os
import sys
import pickle

variables_set = {}
variables_hide = {}
variable_set_time = 0
variable_set_file = "./env.dat"
variable_store_enable = True

class VarTrans:
    """
    Variable Transaction object. Keeps track of whether
    varialbes have been read or written to minimize access
    to the disk.
    """
    def __init__(s):
        s.readF = False
        s.writeF = False
    def __del__(s):
        storevar()
    def read(s):
        global variables_set, variable_set_time, variable_set_file, variables_hide
        if s.readF:
            return
        s.readF = True
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
    def write(s):
        s.writeF = True
def loadvar(tr=None):
    """
    Load all environment variables set with the setvar
    package and print them as they're loaded.
    """
    if tr == None:
        tr = VarTrans()
    tr.read()
    for k in sorted(variables_set):
        v = variables_set[k]
        if k in variables_hide:
            print(k+"=**HIDDEN**")
        else:
            print(k+"="+v)
def showvar(k,tr=None):
    """
    Mark a variable as no longer hidden. If this is done, the variable will
    now display.
    """
    global variables_set, variable_set_time, variable_set_file, variables_hide
    if tr == None:
        tr = VarTrans()
    if k in variables_hide:
        del variables_hide[k]
        tr.write()
def hidevar(k,tr=None):
    """
    Mark a variable as hidden. If this is done, the variable will
    no longer display.
    """
    global variables_set, variable_set_time, variable_set_file, variables_hide
    if tr == None:
        tr = VarTrans()
    if k in variables_hide:
        variables_hide[k]=1
        tr.write()
def repvar(v,tr=None):
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
    if tr == None:
        tr = VarTrans()
    tr.read()
    epos = 0
    buf = ''
    v = str(v)
    for g in re.finditer(r'\$((\w+)|\{([^}]*)\}|\(([^())]*)\))|(\\\$)',v):
        if g:
            i = 2
            while g.group(i) == None:
                i += 1
            p = g.start(0)
            buf += v[epos:p]
            epos = p + len(g.group(0))
            if i == 4:
                #fh = os.popen(g.group(i),"r")
                fh = Popen(repvar(g.group(i),tr),shell=True,close_fds=True,stdout=PIPE,stderr=STDOUT).stdout
                c = repvar(fh.read().decode('utf-8'),tr)
                fh.close()
            elif i == 5:
                c = '$'
            else:
                if g.group(i) == "PID":
                    val = str(os.getpid())
                elif not g.group(i) in os.environ:
                    raise Exception("no such environment variable: "+g.group(i))
                else:
                    val = os.environ[g.group(i)]
                c = repvar(val,tr)
            buf += c
        else:
            break
    buf += v[epos:]
    return buf.strip()
def setvar(e,tr=None):
    """
    setvar() emulates the ability of BASH to set environment variables.
    Thus, NAME=VALUE will set os.environ["NAME"]="VALUE". Bash-style
    comments will be stripped, and bash-line continuations will be processed.
    """
    global variables_set, variable_set_time, variable_set_file, variables_hide
    if tr == None:
        tr = VarTrans()
    tr.read()
    e = re.sub(r'#[^\r\n]*','',e)
    e = re.sub(r'\\\n\s*','',e)
    for m in re.finditer(r'(?m)(\w+)=(.*)',e):
        k = m.group(1)
        v = repvar(m.group(2),tr)
        if k in variables_hide:
            print(k+"=**HIDDEN**")
        else:
            print(k+"="+v)
        if k in variables_set and v == variables_set[k]:
            pass
        else:
            os.environ[k]=v
            tr.write()
            variables_set[k]=v
def storevar():
    """
    Unconditionally store all variables managed with setvar.
    """
    # Make sure the file has the right permissions
    global variable_store_enable
    if variable_store_enable:
        try:
            fd = os.open(variable_set_file,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
            os.close(fd)
            fd = open(variable_set_file,"wb")
            pickle.dump(variables_set, fd)
            pickle.dump(variables_hide, fd)
            fd.close()
            variable_set_time = os.path.getmtime(variable_set_file)
        except PermissionError:
            variable_store_enable = False
            sys.stderr.write("warning: cannot write %s\n" % variable_set_file)
def readfile(f,tr=None):
    """
    Reads in a file. repvar() will be applied to the file name.
    """
    if tr == None:
        tr = VarTrans()
    n = repvar(f,tr)
    print("Reading file `"+n+"'")
    fh = open(n)
    c = fh.read()
    fh.close()
    return c
def writefile(f,c,tr=None):
    """
    Writes out a file. repvar() will be applied both to the file name
    and the file contents.
    """
    if tr == None:
        tr = VarTrans()
    c = str(c)
    n = repvar(f,tr)
    print("Writing file `"+n+"'")
    fd = os.open(n.encode('utf-8'),os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
    os.write(fd,repvar(c,tr).encode('utf-8'))
    os.close(fd)
    #fh = open(n,"w")
    #fh.write(repvar(c))
    #fh.close()
import getpass
def readpass(n,tr=None):
    """
    Read in a password and store it to a file named "n.txt" as well as storing
    it in a variable named "n". If the file exists, however, simpy read it from
    the file.
    """
    global variables_set, variable_set_time, variable_set_file, variables_hide
    if tr == None:
        tr = VarTrans()
    print("Password or secret: "+n)
    f = n+".txt"
    if os.path.exists(f):
        os.environ[n] = readfile(f,tr)
    else:
        os.environ[n] = getpass.getpass()
        writefile(f,"$"+n)
    if n not in os.environ or n not in variables_set or os.environ[n] != variables_set[n]:
        variables_set[n] = os.environ[n]
        variables_hide[n] = 1
        tr.write()
