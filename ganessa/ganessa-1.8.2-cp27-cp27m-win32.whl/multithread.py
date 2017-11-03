# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
'''
Created on 14 déc. 2016

@author: Jarrige_Pi
'''
import time
from datetime import datetime as DT

from multiprocessing import Process, Queue, current_process
from multiprocessing import cpu_count

def snow():
    return DT.now().strftime("%d/%m/%Y %H:%M")

# -------------------------------------
# Definition des fonctions gérant le multithread
# -------------------------------------
#
# Function run by worker processes
#
mpf = '  '
STOP = 'STOP'
def mp_worker(inputqueue, outputqueue):
    for func, args in iter(inputqueue.get, STOP):
        result = mp_calculate(func, args)
        outputqueue.put(result)

#
# Function used to calculate result
#
def mp_calculate(func, args):
    try:
        result = func(*args)
    except Exception as exc:
        result = str(exc)
    return '%s says that %s: %s' % \
        (current_process().name, func.__name__, result)

#
# Function returning the number of active CPU
#
def required_cpu(nb_cpu):
    if nb_cpu <= 0:
        nb_cpu = cpu_count() + nb_cpu
    else:
        nb_cpu = min(nb_cpu, cpu_count())
    return max(1, nb_cpu)
        
#
# Function managing the run queue
#
def mp_run(logprint, tasks, nb_cpu= 3, wait= 1.5):
    # set the threads 
    NUMBER_OF_PROCESSES = max(1, min(required_cpu(nb_cpu), len(tasks)))

    # Create queues
    task_queue = Queue()
    done_queue = Queue()

    # Submit tasks
    for task in tasks:
        task_queue.put(task)
    logprint(mpf + '>>> Task queue built: {} tasks to run'.format(len(tasks)))
    logprint(mpf + '>>> Starting {} threads...'.format(NUMBER_OF_PROCESSES))
    logprint(mpf + '     ' + snow())

    # Tell child processes to stop at the end
    for _i in range(NUMBER_OF_PROCESSES):
        task_queue.put(STOP)

    # Start worker processes
    for _i in range(NUMBER_OF_PROCESSES):
        Process(target=mp_worker, args=(task_queue, done_queue)).start()
        time.sleep(wait)
    logprint('\n' + mpf + '>>> {} threads started.\n'.format(NUMBER_OF_PROCESSES))

    # Get and print results
    for _i in range(len(tasks)):
        retval = done_queue.get()
        logprint(mpf + '>>> ' + retval + '\t ' + snow())

    logprint(mpf + '>>> Threads stopped.')
    logprint(mpf + '     ' + snow())

# the call 'freeze_support()' should appear just after line 
# 'if __name__ == "__main__":' 
# if the script has to be bound to an executable.