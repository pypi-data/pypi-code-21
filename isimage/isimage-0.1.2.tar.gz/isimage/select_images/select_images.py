""" Command line script select_images
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import argparse
from GeneStage import GeneStage
from create_report import create_report
from cPickle import load
from cPickle import dump

import subprocess
import signal
import time
import os
import matplotlib.pyplot as plt
import pandas as pd

sep = os.path.sep

parallel = True
try:
    from IPython.parallel import Client
except:
    parallel = False

def is_number(l):
    try:
        i = int(l)
    except:
        return False
    return True

def job(task_, result, model, compute=None, nc_stage=22, log=None):
    """Run image selection algorithm in GeneStage object"""

    gene, stage, task = task_
        
    try:
        g = GeneStage(gene, stage, task, model, compute=compute, cluster=stage < nc_stage, verbose=False)
        g.save(result)

        return g.dry()
    except:
        e = sys.exc_info()[1]
        if log is not None:
            open(log, 'a').writelines(['Error in '+task[0]+'\n', str(e)+'\n'])
        else:
            raise
        return None

    
def run_jobs_sequentially(ts, result, model, compute=None, nc_stage=22, log=None):
    return [job(t, result, model, compute, nc_stage=nc_stage, log=log) for t in ts]

def run_jobs_parallel(ts, result, model, compute=None, nc_stage=22, log=None):
    assert(compute is not None)
    compute.execute('from select_images import job')
    return compute.map(lambda par: job(*par), zip(ts, [result]*len(ts), [model]*len(ts), [None]*len(ts), [nc_stage]*len(ts), [log]*len(ts))).result 

def main():
    parser = argparse.ArgumentParser(description='Selects best stained representative images from gene/stage groups.')
    parser.add_argument('-g', '--genestages', metavar='file_name', type=str, nargs=1, help='tab delimited file containing gene names, stages, and image file names') 
    parser.add_argument('-r', '--result', metavar='folder_name', type=str, nargs=1, help='path to the result folder') 
    parser.add_argument('-c', '--cleared_model', metavar='file_name', type=str, nargs=1, help='path to pickled model predicting if the image was cleared') 
    parser.add_argument('-l', '--log', metavar='file_name', type=str, nargs=1, help='path to log file') 
    parser.add_argument('-s', '--noncluster_stage', dest='stage', metavar='stage', type=float, default=[22], nargs=1, help='The earliest stage which is not clustered on expression patterns. default: 22')     
    if parallel:
        parser.add_argument('-p', '--parallel_images', metavar='N', type=str, nargs=1
            , help='the number of threads or path to ipcontroller-client.json. Images in gene/stage groups are analysed in parallel with the gene/stage groups processed sequentially. Memory footprint is O(1) times bigger compared to single threaded run.') 
        parser.add_argument('-j', '--parallel_genestages', metavar='N', type=str, nargs=1
            , help='the number of threads or path to ipcontroller-client.json. Images in gene/stage groups are analysed sequentially with the gene/stage groups processed in parallel. Memory footprint is O(N) times bigger compared to single threaded run.') 
        
    args = parser.parse_args()
    
    if not (args.genestages and args.result):
        print('Error: No action requested, please specify at least input files and output folder')
        args = parser.parse_args(["--help"])
        
    if args.log is None:
        args.log = [None]
        
    if args.cleared_model is None:
        args.cleared_model = [None]

    if args.stage is None:
        args.stage = [22]
        
    #check if parallel run is avalible and requested
    compute = None
    run_jobs = run_jobs_sequentially
    stop_cluster = False
    if parallel and (args.parallel_images or args.parallel_genestages): 
        if args.parallel_genestages:
            run_jobs = run_jobs_parallel
            N = args.parallel_genestages[0]
        else:
            N = args.parallel_images[0]
        
        #start ipython parallel cluster and connect to it
        if is_number(N):
            subprocess.Popen(["ipcluster", "start", "-n", N, "--quiet"])#
            
            c = None
            while c is None:
                time.sleep(.1)
                try:
                    c = Client()
                except:
                    continue
            
            n = int(N)
            while len(c.ids) != n:
                time.sleep(.1)
            
            compute = c[:]
            stop_cluster = True
        else:
            compute = Client(N)[:]
            compute.execute('import os;os.chdir("'+os.getcwd()+'")')    
            
        compute.execute('import isimage')
    
    #read image list
    input_tab = pd.read_table(args.genestages[0], sep='\t', header=None, names=['gene', 'stage', 'image'])

    base_path = os.path.abspath(os.path.split(args.genestages[0])[0])
    tasks = []
    for g in set(input_tab['gene']):
        for s in set(input_tab[input_tab['gene'] == g]['stage']):
            tasks += [[g, float(s), [os.path.abspath(sep.join([base_path, '.', f])) if (not os.path.isabs(f)) else f for f in list(input_tab[(input_tab['gene'] == g) & (input_tab['stage'] == s)]['image'])]]]
     
    #run image selection algorithm
    try:
        gs = run_jobs(tasks, args.result[0], args.cleared_model[0], compute=compute, nc_stage=args.stage[0], log=args.log[0])
    except:
        raise
    finally:
        if stop_cluster:
            subprocess.Popen(["ipcluster", "stop", "--quiet"])
        
    dump(gs, open(os.path.join(args.result[0], 'gs.dump'), 'w'))
    
    create_report(os.path.join(args.result[0], 'result.html'), [g for g in gs if g is not None])

    

if __name__ == '__main__':
    main()

