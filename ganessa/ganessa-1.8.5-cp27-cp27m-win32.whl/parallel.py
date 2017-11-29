# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
'''
Created on 16 nov. 2017

@author: Jarrige_Pi
'''
import time
from datetime import datetime as DT
from itertools import chain

from multiprocessing import Process, Queue, current_process
from multiprocessing import cpu_count

def snow():
    return DT.now().strftime("%d/%m/%Y %H:%M:%S")

# -------------------------------------
# Parallelism handling functions 
# -------------------------------------
#
# Function run by worker processes
#
STOP = 'STOP'
TEMPO = 0.125
def mp_worker(inputqueue, outputqueue, init, term, wait, wpnum, wpcount, use):
    '''worker loop for a a parallel process'''
    # rank init and term < 0 for sorting
    if init is not None:
        func, args = init
        rank = -wpnum
        sres, result = mp_calculate(func, args, rank, -1, wpnum, use)
        outputqueue.put((rank, sres, result))
        time.sleep(TEMPO)
    # count is used for logging and temporisation of 1st task
    for count, rankedtask in enumerate(iter(inputqueue.get, STOP)):
        if not count:
            time.sleep(wait)
        rank, (func, args) = rankedtask
        sres, result = mp_calculate(func, args, rank, count, wpnum, use)
        outputqueue.put((rank, sres, result))
    # rank init and term < 0 for sorting
    if term is not None:
        TMARK = 10 if wpcount < 10 else 100 if wpcount < 100 else 1000
        func, args = term
        rank = -wpnum - TMARK
        sres, result = mp_calculate(func, args, rank, -2, wpnum, use)
        outputqueue.put((rank, sres, result))
    outputqueue.close()

#
# Function used to run each task and summarize result
#
def mp_calculate(func, args, rank, count, wpnum, use):
    try:
        result = func(*args, wpnum=wpnum) if use else func(*args)
        stat = result if isinstance(result, basestring) else 'Ok!'
    except Exception as exc:
        result = None
        stat = str(exc)
    sres = '{} [run {:2d}] says that {}({:2d}): {}'.format(
            current_process().name, count, func.__name__, rank, stat)
    return sres, result

#****g* ganessa.parallel/About
# PURPOSE
#   The module ganessa.parallel provides a multitasking (parallel) computing
#   capability based on multiprocessing Process and Queue objects.
#****

#****g* ganessa.parallel/Classes_p
#****
#****g* ganessa.multithread/Functions_m
#****

#****f* Functions_p/required_cpu
# SYNTAX
#   ncpu = required_cpu(nb_cpu)
# ARGUMENT
#   int nb_cpu: expected number of parallel processes, up to the hardware core count. 
#   A negative or null value indicates the number of hardware cores + nb_cpu.
# RESULT
#   int ncpu: actual number of parallel processes (1 ... max physical core count)
# EXAMPLE
#   * required_cpu(-1) returns the hardware core count but one.
#****
def required_cpu(nb_cpu):
    return 1 + max(0, (nb_cpu - 1) % cpu_count())

#****o* Classes_p/MultiProc, run, run_sequential
# DESCRIPTION
#   The MultiProc class allows to define and run tasks in parallel. A number
#   of N processing instances (nb_cpu provided, default all cores but one)
#   are created; then tasks from the tasks list are dispatched to the processing
#   instances. 
#
#   An init task (resp. a term task) may be provided; if so it is called by
#   each processing instance before the 1st task (resp. after the last one).
#   If init is not provided, 
#   first N tasks are guaranteed to be run on distinct instances and 
#   can also be used for initialisation purposes. Then each task in the list is
#   associated to the next processing instance available in turn. The execution
#   order is not guaranteed (except the first N tasks if init is not provided).
#
#   run executes the tasks list in parallel ptrocessing instances; run_sequential 
#   executes the tasks list sequentially, i.e. init, tasks in order, term.
#
# SYNTAX
#   * mp = MultiProc(logprint [, nb_cpu= -1] [, wait= 0.0] [, use_wpnum= False])
#   * results, resinit, resterm = mp.run(tasks [, init=None] [, term= None])
#   * results, resinit, resterm = mp.run_sequential(tasks [, init=None] [, term= None] [, wpnum= None])
#   * ncpu = mp.nmaxcpu
# ARGUMENT
#   * function logprint: called by mp.run with a single str arg for logging 
#   * int nb_cpu: optional number of parallel processes, up to the hardware core count. 
#     A negative value indicates the number of hardware cores + nb_cpu (defaults to -1).
#   * float wait: wait time (s) before the first task of each processing instance.
#   * bool use_wpnum: if True, the function called in task list must accept an
#     integer keyword argument wpnum, being equal to the process number (1 ... nb_cpu)
#     in charge of its execution.
#   * tasks: list of (func, args) tuples defining the tasks to be run as func(*args) if
#     use_wpnum is False or not set; or func(*args, wpnum= proc_num) otherwise.
#     if func returns a str or unicode, it will be inserted in the log string.
#   * init (optional) tuple (func, args) to be called by every processing instance
#     before any tasks.
#   * term (optional) tuple (func, args) to be called by every processing instance
#     after all tasks.
# RESULT
#   * results: list of result = func(args), in the original tasks list order.
#   * resinit: list of results for init calls (empty if init is None).
#     Its length is the processing instances count.
#   * resterm: list of results for term calls (empty if term is None).
#     Its length is the processing instances count.
#   * int ncpu: number of processing instances.
# REMARKS
#   * tasks are run in parallel by the set of parallel processes: when a process
#     ends up a task, it starts executing the next task available in the list. 
#   * the number of processing instances is available as mp.nmaxcpu
#   * run_sequential is provided for debugging, it loops and execute tasks in turn.
#   * if the tasks count is smaller than the number of requested cpus, the number 
#     of processing instances is reduced to the task count.
# HISTORY
#   * Created 2016.12.14 
#   * Updated 2017.11.14: class interface and optional wpnum argument. 
#   * Updated 2017.11.17: renamed to parallel; added results return list.
#     added init and term options
#   * Updated 2017.11.20: return values as a tuple of 3 lists for tasks, init, term
#****

# class for encapsulating the thing
class MultiProc(object):
    def __init__(self, logprint, nb_cpu= -1, wait= 0.0, use_wpnum= False):
        self.logfun = logprint
        self._nmaxcpu = required_cpu(nb_cpu)
        # first tasks must be taken by workers before any one ends up.
        self.wait = wait
        self.use_wpnum = use_wpnum
        
    @property
    def nmaxcpu(self):
        '''Get the max used CPU count'''
        return self._nmaxcpu
        
    def run(self, tasks, init= None, term= None):
        '''Runs tasks list in parallel'''
        # set the threads 
        mpf = '  >>> '
        ntasks = len(tasks)
        self.ncpu = min(self._nmaxcpu, ntasks)
        if not tasks:
            return
        if self._nmaxcpu == 1:
            return self.run_sequential(tasks)
    
        # Create queues
        task_queue = Queue()
        done_queue = Queue()
    
        logprint = self.logfun
        # Submit tasks and remember initial rank
        logprint(mpf + snow())
        for rank, task in enumerate(tasks):
            task_queue.put((rank, task))
        logprint(mpf + 'Task queue built: {} tasks to run'.format(ntasks))
    
        # Tell child processes to stop at the end
        for _i in range(self.ncpu):
            task_queue.put(STOP)
    
        # Create worker processes
        logprint(mpf + 'Creating {} threads...'.format(self.ncpu))
        # introduce delay for 1st task of wp if no explicit init
        wait = max(self.wait, TEMPO) if init is None else self.wait
        processes = [Process(target= mp_worker, 
                             args= (task_queue, done_queue, init, term,
                                    wait, pn+1, self.ncpu, self.use_wpnum))
                             for pn in range(self.ncpu)]
        # Start worker processes
        for p in processes:
            p.start()
        logprint('\n' + mpf + '{} threads started.\n'.format(self.ncpu))
    
        # Get and print results asap
        results = []
        if init is not None:
            ntasks += self.ncpu
        if term is not None:
            ntasks += self.ncpu
            
        for _i in range(ntasks):
            input_rank, retlog, retval = done_queue.get()
            logprint(mpf + retlog + '\t ' + snow())
            results.append((input_rank, retval))
    
        # Wait for worker processes to stop
        for p in processes:
            p.join()
            p.terminate()
        del task_queue, done_queue 
        logprint(mpf + 'Threads stopped.')
        
        # sort results by initial task rank (term, init, tasklist)
        results.sort()
        logprint(mpf + snow())
        # returns results only, not rank
        results = zip(*results)[1]
        # extract init and term results
        nt = 0 if term is None else self.ncpu
        ni = nt if init is None else nt + self.ncpu
        return results[ni:], results[nt:ni], results[:nt]
    
    def run_sequential(self, tasks, init= None, term= None, wpnum=0):
        '''Run tasks list sequentially'''
        # define calculation function
        def seq_calculate(func, args): 
            if self.use_wpnum:
                result = func(*args, wpnum=wpnum)
            else:
                result = func(*args)
            stat = result if isinstance(result, basestring) else 'Ok!'
            self.logfun(func.__name__ + ' ' + stat)
            return result
        
        resinit, resterm = [], []
        if init is not None:
            resinit = [seq_calculate(*init)]
        results = [seq_calculate(*task) for task in tasks]
        if term is not None:
            resterm = [seq_calculate(*term)]
        return results, resinit, resterm
           
# the call 'freeze_support()' should appear just after line 
# 'if __name__ == "__main__":' 
# if the script has to be bound to an executable.