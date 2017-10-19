from hdflog import (PROCGRAPH_LOG_GROUP, check_is_procgraph_log,
    tc_open_for_reading, tc_close)
from procgraph import Block, Generator, BadConfig
import glob
import numpy
import operator
import os


__all__ = ['HDFread_many']


class HDFread_many(Generator):
    ''' 
        This block is a variation on :ref:`block:hdfread` that can 
        concatenate the output of logs stored in multiple HDF files.
        
        The files are specified using a wildcard: for example, ``dir/*.h5``.
        
        A difference with :ref:`block:hdfread` is that all signals
        must be specified explicitly (:ref:`block:hdfread` can guess); the
        reason is that we want to avoid reading unrelated logs with different
        signals.
        
        We check that all files specified have all required signals.
        
        The logfiles are read in the order compatible with their timestamp.
    '''
    Block.alias('hdfread_many')
    Block.output_is_defined_at_runtime('The signals read from the logs.')

    Block.config('files', 'HDF files to read; you can use the wildcard ``*``.')
    Block.config('signals', 'Which signals to output (and in what order). '
                 'Should be a comma-separated list. ')

    Block.config('quiet', 'If true, disables advancements status messages.',
                 default=False)

    def get_output_signals(self):
        self.signals = filter(lambda x: x, self.config.signals.split(','))
        if not self.signals:
            raise BadConfig('No signals specified.', self, 'signals')
        return self.signals

    def init(self):
        # Find the required files
        files = glob.glob(self.config.files)

        if len(files) == 0:
            raise BadConfig('No files correspond to the pattern %r.'
                            % self.config.files, self, 'files')

        # Open all logs; make sure they have the required signals and
        # note their initial timestamp.

        # list(tuple(file, timestamp, signal2table))
        logs = []
        for f in files:
            hf = tc_open_for_reading(f)
            check_is_procgraph_log(hf)

            log_group = hf.root._f_getChild(PROCGRAPH_LOG_GROUP)
            log_signals = list(log_group._v_children)

            signal2table = {}
            for s in self.signals:
                if not s in log_signals:
                    raise Exception('Log %r does not have signal %r '
                                    '(it has %s).' % (f, s, log_signals))
                signal2table[s] = log_group._f_getChild(s)

            timestamp = signal2table[s][0]['time']
            logs.append((hf, timestamp, signal2table))

        # Sort them by timestamp
        self.logs = sorted(logs, key=operator.itemgetter(1))
        self.current_log = None

        for log in logs:
            filename = log[0].filename
            length = len(list(log[2].values())[0])
            self.status('- queued log (%6d rows) from %r' % (length, filename))

        self.start_reading_next_log()

    def status(self, s):
        if not self.config.quiet:
            self.info(s)

    def start_reading_next_log(self):
        if self.current_log is not None:
            self.status('Just finished log %r.' % self.current_log[0].filename)
            tc_close(self.current_log[0])
            self.current_log = None

        if not self.logs:
            # we finished
            self.status('No logs remaining.')
            return

        self.current_log = self.logs.pop(0)
        self.signal2table = self.current_log[2]

        self.status('Now starting with %r.' % self.current_log[0].filename)

        # signal -> index in the table (or None)
        self.signal2index = {}

        for signal in self.signals:
            if len(self.signal2table[signal]) > 0:
                self.signal2index[signal] = 0
            else:
                self.signal2index[signal] = None

    def _choose_next_signal(self):
        ''' Returns a tuple (name,timestamp) of the signal that produces 
            the next event, or (None,None) if we finished the log. '''
        # array of tuples (signal, timestamp)
        status = []
        for signal in self.signals:
            index = self.signal2index[signal]
            if index is not None:
                table = self.signal2table[signal]
                timestamp = table[index]['time']
                status.append((signal, timestamp))

        if not status:
            return (None, None)
        else:
            sorted_status = sorted(status, key=operator.itemgetter(1))
            return sorted_status[0]

    def next_data_status(self):
        next_signal, next_timestamp = self._choose_next_signal()
        if next_signal is None:
            # one log is finished:
            if not self.logs:
                # no more logs
                return (False, None)
            else:
                self.start_reading_next_log()
                return self.next_data_status()
        else:
            return (True, next_timestamp)

    def update(self):
        next_signal, next_timestamp = self._choose_next_signal()
        assert next_signal is not None

        # get value
        table = self.signal2table[next_signal]
        index = self.signal2index[next_signal]
        assert next_timestamp == table[index]['time']
        value = table[index]['value']

        self.set_output(next_signal, value=value, timestamp=next_timestamp)

        # update index
        if index + 1 == len(table):
            # finished
            self.status('Finished reading signal %r.' % next_signal)
            self.signal2index[next_signal] = None
        else:
            self.signal2index[next_signal] = index + 1

        # Status messages for the first signal
        if next_signal == self.signals[0]:
            T = len(table)
            nintervals = 10
            interval = int(numpy.floor(T * 1.0 / nintervals))
            if (index > 0 and index != interval * (nintervals) and
                 index % interval == 0):
                percentage = index * 100.0 / T

                T = str(T)
                index = str(index).rjust(len(T))
                self.status('Read %.0f%% (%s/%s) of %r (tracking signal %r).' % 
                            (percentage, index, T,
                             os.path.basename(self.current_log[0].filename),
                             next_signal))

    def finish(self):
        self.start_reading_next_log()

