import os
import subprocess
import time


def Run(inputfile, jobname='file', nproc=4, outname='output.txt', memory=0,
        batch=False, rundir='', print_input=False):
    """ Runs ANSYS """

    if rundir:
        olddir = os.getcwd()
        os.chdir(rundir)

    # Check if input file exists
    if not os.path.isfile(inputfile):
        if rundir:
            os.chdir(olddir)
        raise Exception('Input file does not exist')

    if os.path.isfile(jobname + '.lock'):
        if rundir:
            os.chdir(olddir)
        raise Exception('Lock file exists for jobname ' + jobname)

    # add options
    options = ''
    options += '-j {:s} '.format(jobname)
    options += '-np {:d} '.format(nproc)
    options += '-o {:s} '.format(outname)
    options += '-i "{:s}" '.format(inputfile)
    if batch:
        options += '-b '

    if memory:
        options += '-m {:d} '.format(memory)

    command = "/usr/ansys_inc/v150/ansys/bin/ansys150 {:s}".format(options)
    if print_input:
        print(command)
    subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)

    # wait until the lock
    time.sleep(1)
    while os.path.isfile(jobname + '.lock'):
        time.sleep(0.1)

    if rundir:
        os.chdir(olddir)
