import signal


def sig_enumerate(seq, start=0, logger=None):
    '''
    Just like the built-in enumerate(), but also respond to SIGINFO (Ctrl-T) with a
    line of output to the given / default logger.
    '''
    if logger is None:
        import logging
        logger = logging.getLogger('SIGINFO')

    message = 'Iteration: -1'

    def handler(signum, frame):
        logger.info(message)

    logger.debug('enumerating... type Ctrl-T to show current iteration')

    signum = signal.SIGINFO
    old_handler = signal.signal(signum, handler)
    try:
        for i, x in enumerate(seq, start=start):
            message = 'Iteration: %d' % i
            yield i, x
    finally:
        # put the original signal back
        signal.signal(signum, old_handler)


def take(seq, n):
    '''
    Basically just itertools.islice(seq, 0, n)
    '''
    last_index = n - 1
    # return itertools.islice(seq, n)
    for index, item in enumerate(seq):
        yield item
        if index == last_index:
            break


def iside(seq, fn):
    '''
    Wrap an iterable with side effects, yielding the input unchanged.
    `fn` will be called as `fn(index, item)` for each `item` in `seq`

    E.g.:

        # print to STDERR to avoid buffering
        import sys
        def tell(index, item):
            if index % 100 == 0:
                print >> sys.stderr, index,

        total = 0
        for x in iside(xrange(10000), tell):
            total += sum(range(1, x))
        print 'total', total

    '''
    for index, item in enumerate(seq):
        fn(index, item)
        yield item


def isplit(seq, fn):
    '''
    Create two lists containing all items in seq,
    depending on the result of calling fn on each item.
    Returns a tuple of (seq where true, seq where false)

    Turns out there's not really a nice, elegant way to do this when iterating
    over the list only once. See https://stackoverflow.com/q/949098

    But, hmm, this might be better:
    from itertools import tee
    def split_on_condition(seq, condition):
        l1, l2 = tee((condition(item), item) for item in seq)
        return (i for p, i in l1 if p), (i for p, i in l2 if not p)
    '''
    true = []
    false = []
    for item in seq:
        if fn(item):
            true.append(item)
        else:
            false.append(item)
    return true, false
