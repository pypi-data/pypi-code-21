#!/usr/local/bin/python
import io, nbformat, subprocess;
import sys, os, importlib, inspect
from default_ws_config import *
#import wsUtils

import psutil

def kill(cmd0=None, cmd1=None):
    pass;

def findPS(cmd0=None, cmd1=None):
    if (cmd0 is None and cmd1 is None):
        return
    
    for proc in psutil.process_iter():
        try:
            n = proc.name()
            cmd = proc.cmdline()
            if ( (cmd0 and cmd[0].find(cmd0) > 0 ) or
                 (cmd1 and cmd[1].find(cmd1) > 0 )  ):
                print ("Found process ", n, cmd, proc.pid )
                return proc
        except:
            pass

    return None

def bookKeeping():
    global notebooks
    cwd=os.getcwd()
    sys.path.append(cwd)
    if (os.path.islink(sys.argv[0])):
        link = os.readlink(sys.argv[0])
        sys.path.append(os.path.dirname(link))

def deploy():
    global notebooks
    global port

    if ( len(sys.argv) > 1 ):
        print ("Importing from ", sys.argv[1]);
        im = importlib.import_module(sys.argv[1])
        notebooks = im.notebooks
        port = im.port

    merge_notebooks(notebooks, 'wsex.ipynb', False);

def run():
    global port
    proc = findPS(cmd1='jupyter-kernelgateway')
    if ( proc is not None):
        print("Process seems to be running ...")
        return

    OPTS='--KernelGatewayApp.api="kernel_gateway.notebook_http" --KernelGatewayApp.prespawn_count=1'
    PORT='--KernelGatewayApp.port=' + str(port)
    URI='wsex.ipynb'
    URI1='--KernelGatewayApp.seed_uri='+URI

    oss = "jupyter kernelgateway {} {} {}".format(OPTS, PORT, URI1)
    print ("Starting ", oss);
    p = subprocess.run(oss , shell=True)
    #p = subprocess.Popen("./kg.sh" )
    #p.wait()

def merge_notebooks(filenames, outf = None, printO=False):
    merged = None
    for fname in filenames:
        print("Merging ", fname, " ...");
        with io.open(fname, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        if merged is None:
            merged = nb
        else:
            # TODO: add an optional marker between joined notebooks
            # like an horizontal rule, for example, or some other arbitrary
            # (user specified) markdown cell)
            merged.cells.extend(nb.cells)
    if not hasattr(merged.metadata, 'name'):
        merged.metadata.name = ''
    merged.metadata.name += "_merged"

    if (printO):
        print(nbformat.writes(merged))
    if (outf is not None):
        print("Writing to file ", outf, " ...")
        with( io.open(outf, "w", encoding='utf-8')) as mf:
            mf.write(nbformat.writes(merged))


# Command line merge tool
def cmd():
    notebooks = sys.argv[1:]
    if not notebooks:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
        
    merge_notebooks(notebooks)

def test():
    try:
        im = importlib.import_module('myconfig');
        po = im.port
        nb = im.notebooks
    except:
        po = "NONE"
        nbs= "NONE"
        pass;


    print ("Port: " , po)

if __name__ == '__main__':
    if ( len(sys.argv) > 1 and sys.argv[1] == 'test'):
        test()
        exit();
    bookKeeping()
    deploy();
    run();
