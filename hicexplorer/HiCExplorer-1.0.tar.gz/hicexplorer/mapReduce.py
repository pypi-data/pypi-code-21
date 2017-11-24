import multiprocessing
import numpy as np

def mapReduce(staticArgs, func, list_contig_sizes,
              contig_list_length=None, 
              region=None,
              numberOfProcessors=4,
              verbose=False):

    """
    Split the genome into parts that are sent to workers using a defined
    number of procesors. Results are collected and returned.

    For each genomic region the given 'func' is called using
    the following parameters:

     contigList, staticArgs

    The *arg* are static, *pickable* variables that need to be sent
    to workers.

    The contigList length corresponds to the number of
    contigs that should be processed by each worker.

    Depending on the type of process a larger or shorter regions may be 
    preferred

    :param list_contig_sizes: A list of duples containing the contig id and its length
    """

    if not contig_list_length:
        contig_list_length = len(list_contig_sizes) / numberOfProcessors
        
    if verbose:
        print "contigs per worker: %s" % (contig_list_length) 

    TASKS = []
    # iterate over all contigs
    contig_list, size = zip(*list_contig_sizes)
    contig_blocks = np.array_split(contig_list, numberOfProcessors)
    for contig_list in contig_blocks:
        argsList = [contig_list.tolist()]
        argsList.extend(staticArgs)
        TASKS.append( tuple(argsList) )

    if len(TASKS) > 1 and numberOfProcessors>1:
        if verbose:
            print ("using {} processors for {} "
                   "number of tasks".format(numberOfProcessors,
                                            len(TASKS)))

        pool = multiprocessing.Pool(numberOfProcessors)
        res = pool.map_async( func, TASKS ).get(9999999)
    else:
        res = map(func, TASKS)

    return res
