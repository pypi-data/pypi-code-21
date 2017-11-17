
import multiprocessing
from functools import partial
import time, timeit, sys
from multiprocessing.dummy import Pool as ThreadPool

from .time import estimate_time

def abortable_worker(func, *args, **kwargs):
    """
    For use with parallel_loop_with_timeout. 
    """
    timeout = kwargs.get('timeout', None)
    del kwargs['timeout']
    p = ThreadPool(1)
    res = p.apply_async(func, args=args, kwds=kwargs)
    try:
        out = res.get(timeout)  # Wait timeout seconds for func to complete.
        return out
    except multiprocessing.TimeoutError:
        print("Aborting due to timeout")
        p.terminate()
        return 'timeout'

def parallel_loop_with_timeout(target, iterlist, timeout=2, **kwargs):
    """
    Parallelizes a loop while imposing a timeout on any individual iteration of the loop. Returns a list
    of tuples where the first elements are the index of iterlist and the second elements are the results.
    If any iteration times out, will still add the tuple to the list but the second element will be 
    'timeout'. 
    
    IMPORTANT NOTE:
    The target function MUST BE IMPORTED. This will not work if you define the target function in your
    current namespace. This is a multiprocessing restriction. The function can be imported from the same
    module as this paralellizing function.
    
    Arguments:
    target: function, must be imported. Must accept one regular argument, for which the function will
            be evaluated for each element of iterlist. Any additional arguments which do not change with
            each iteration must be passed as keyword arguments.
    iterlist: list, arguments to pass to target function. Will call the target function one time for
              each element of the list.
    timeout: int, maximum time to wait for each function call.
    **kwargs: include any keyword arguments to pass to target function 
    
    """
    counter = []
    
    pool = multiprocessing.Pool()
    abortable_func = partial(abortable_worker, target, timeout=timeout)
    
    start_time = timeit.default_timer()
    num_loops = len(iterlist)
    
    
    results = [(i,
              pool.apply_async(abortable_func, args=(arg,), kwds=kwargs, callback=counter.append))
              for i, arg in enumerate(iterlist)]
    pool.close()
    
    try: 
        while len(counter) != num_loops:
            estimate_time(num_loops, len(counter), start_time)
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pool.terminate()
        pool.join()
        print('Exiting.')
        sys.exit(1)

    pool.join()
    return [(result[0], result[1].get()) for result in results]