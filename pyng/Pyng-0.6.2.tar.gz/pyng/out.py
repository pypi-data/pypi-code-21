#!/usr/bin/python
"""
    out.py                           Nat Goodspeed
    Copyright (C) 2015               Nat Goodspeed

Python generators imply a natural composition idiom:

def filter(iterable):
    for item in iterable:
        # do something and then
        yield item

Such generators can readily be chained to construct arbitrary pipelines.

The introduction of reverse data flow ('yield' returning a result) permits
chains of output generators as well. Which processing belongs in an input
chain and which in an output chain? The answer depends on where you put the
driving loop. For example:

    from pyng.genio import filesink, filesource
    filesink(outname, filter(filesource(inname)))

The above chain is driven by the loop in filesink(), the ultimate destination.
Therefore all the rest of the processing can be performed using input
generators.

I have yet to encounter an equally obvious idiom for output chains. (To be
fair, the community may have adopted one without my being aware of it.) One
reasonable choice is to base the API on file-like objects, at least a subset
of the output-related methods:

class ofilter(object):
    def __init__(self, sink):
        self.sink = sink

    def write(self, item):
        # do something and then
        self.sink.write(item)

    def flush(self):
        self.sink.flush()

Though the above trivial filter doesn't require output-generator
machinery, it supports it. (See, for example, buffer_lines below.)

Such output filters can be composed as:

    with open(outname, 'w') as outf:
        sink = ofilter1(ofilter2(outf))
        for line in open(inname):
            sink.write(line)

NRG 2015-11-07
"""

import syslog

class OutError(Exception):
    pass

class ofilter(object):
    """
    The output filter API is primarily write() and (optionally) flush(). But
    it can be convenient to emulate other file-like output methods, permitting
    your filter to be passed to functions expecting an open output file.
    Derive from this class, overriding whatever you need.
    """
    def __init__(self, sink=None, **kwds):
        self.sink = self._maybe_adapt(sink, **kwds)

    def _maybe_adapt(self, sink=None, **kwds):
        """
        We expect the passed sink to be itself a file-like object, at least to
        the extent of supporting write() and flush(). But we facilitate one
        other use case: a sink consisting of a unary callable. For instance,
        you might pass write=mylist.append as the sink to one of our
        subclasses. Therefore subclasses should call this method to properly
        interpret their sink param.
        """
        try:
            write = kwds.pop("write")
        except KeyError:
            # No write= override: does the sink parameter have a write()
            # method?
            try:
                sink.write
            except AttributeError:
                raise OutError("%s passed invalid sink %s" %
                               (self.__class__.__name__, sink.__class__.__name__))
            # sink has a write() method, how about flush()?
            try:
                sink.flush
            except AttributeError:
                # Caller will expect flush(). Construct an adapter whose
                # write() will call sink.write(), and whose flush() is a
                # no-op.
                return adapter(sink.write)
            else:
                # sink has both write() and flush(), use it directly
                return sink
        else:
            # Caller explicitly passed write=something. Construct an adapter
            # with the caller's write() and perhaps flush() callables.
            return adapter(write, kwds.pop("flush", None))

    def write(self, item):
        # do something and then
        self.sink.write(item)

    def writelines(self, iterable):
        for item in iterable:
            self.write(item)

    def flush(self):
        self.sink.flush()

    def close(self):
        self.flush()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()
        # don't eat any exception
        return False

class adapter(ofilter):
    """
    Wrap an arbitrary write() callable (and perhaps a separate flush()
    callable) as a file-like object.
    """
    def __init__(self, write, flush=None):
        # We do not forward the call to base-class __init__(), therefore we
        # have no self.sink attribute.
        self.write = write
        if flush:
            self.flush = flush

    def flush(self):
        # Have to override flush() method so we don't call base-class one that
        # references self.sink.
        pass

class _Flush(Exception):
    """Exception used internally by buffer_lines"""
    pass

class buffer_lines(ofilter):
    """
    Certain output libraries (e.g. syslog) produce a distinct line of output
    for each call. While you can readily fake up a file-like object whose
    write() method writes to syslog, the fact that Python I/O frequently
    writes partial lines can be a problem. An ordinary print statement calls
    write() at least twice: once for each item, once for the space implied by
    each comma between items, with a final call for the newline character.
    pprint.pprint() writes each item separately.

    This output filter assembles complete lines from multiple calls.
    """
    def __init__(self, sink=None, **kwds):
        """
        Pass eol='\n' if you want a newline on each line passed through
        sink(). Otherwise the newline character is eaten.
        """
        self.eol = kwds.pop("eol", '')
        self.loopgen = self.loop(self._maybe_adapt(sink, **kwds))
        # Run self.loop() up to the first yield. Discard the None.
        self.loopgen.next()

    def write(self, item):
        # cause loop()'s (yield) to return the passed item
        self.loopgen.send(item)

    def flush(self):
        # pending buffer can be flushed simply by sending a newline
        self.write('\n')
        # but then also flush sink
        self.loopgen.throw(_Flush)

    def loop(self, sink):
        # start with an empty string so we always have a buffer[-1]
        buffer = [""]
        # loop forever
        while True:
            # until the most recent item contains at least one newline
            while '\n' not in buffer[-1]:
                try:
                    # accumulate items
                    buffer.append((yield))
                except _Flush:
                    sink.flush()
            # buffer[-1] contains at least one newline: time to flush!

            # Remove that last item from buffer and split on newlines. Remove
            # any stray '\r' at the end of each piece.
            pieces = [p.rstrip('\r') for p in buffer.pop(-1).split('\n')]
            # Even '\n'.split('\n') generates ['', '']. In general there are
            # three sections in the resulting list:

            # pieces[0] (possibly empty) is the tail end of the partial line
            # we've been accumulating in buffer. Remove it from pieces,
            # assemble the whole line and emit it. Recall that there's no
            # newline in any string in buffer[:-1], because we always flush
            # buffer as soon as buffer[-1] contains a newline.
            sink.write(''.join(buffer + [pieces.pop(0), self.eol]))

            # pieces[-1] (possibly empty) is the fragment at the start of the
            # next partial line. Remove it from pieces and capture in buffer
            # for later.
            # This is where the distinction between splitlines() and
            # split('\n') becomes important. 'abc\n'.splitlines() returns
            # simply ['abc'], while 'abc\n'.split('\n') returns ['abc', ''].
            # The latter is essential if we are to properly handle an item
            # with a dangling partial line fragment.
            buffer = [pieces.pop(-1)]

            # The remaining middle of pieces is the list (possibly empty) of
            # unbroken lines from the most recent (yield) expression. And yes,
            # '\n\n' pairs will send an empty line through sink.write().
            for line in pieces:
                sink.write(line + self.eol)

            # Loop back to accumulate more fragments in buffer.

class _syslogger(ofilter):
    """
    An instance of this class is a 'file-like object' whose write() method
    writes to syslog.
    """
    def __init__(self, *args, **kwds):
        """
        Constructor accepts syslog.openlog() arguments, plus a keyword-only
        argument level= [default syslog.LOG_INFO] which will be passed to each
        syslog.syslog() call along with the text.
        """
        # remove level= from kwds so openlog() won't crump
        self.level = kwds.pop("level", syslog.LOG_INFO)
        # forward all remaining arguments to openlog()
        syslog.openlog(*args, **kwds)

    def write(self, text, **kwds):
        # Accept an extension keyword-only level= parameter. Unless you
        # override it in this write() call, the default log level is as
        # specified to our constructor.
        syslog.syslog(kwds.pop("level", self.level), text)

    def flush(self):
        pass

def syslogger(*args, **kwds):
    """
    Wrap _syslogger so that we properly buffer lines to go to the log.
    """
    return buffer_lines(_syslogger(*args, **kwds))
