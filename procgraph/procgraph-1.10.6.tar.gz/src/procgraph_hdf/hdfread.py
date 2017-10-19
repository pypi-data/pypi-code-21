import operator

from procgraph  import Block, Generator, BadConfig

import numpy
from hdflog.tables_cache import tc_close

    # TODO: check there is at least one signal

# TODO: respect original order


class HDFread(Generator):
    ''' 
        This block reads a log written with :ref:`block:hdfwrite`.
    
    '''
    Block.alias('hdfread')
    Block.output_is_defined_at_runtime('The signals read from the log.')
    Block.config('file', 'HDF file to read')
    Block.config('signals', 'Which signals to output (and in what order). '
                 'Should be a comma-separated list. If you do not specify it '
                 ' will be all signals (TODO: in the original order).',
                 default=None)

    Block.config('quiet', 'If true, disables advancements status messages.',
                 default=False)

    def get_output_signals(self):
        self.reader = self.config.file 
        all_signals = self.reader.get_all_signals()
        
        if self.config.signals is None:
            self.signals = all_signals
        else:
            signal_list = filter(lambda x: x, self.config.signals.split(','))
            if not signal_list:
                msg = 'Bad format: %r.' % self.config.signals
                raise BadConfig(msg, self, 'signals')
            for s in signal_list:
                if not s in all_signals:
                    msg = ('Signal %r not present in log (available: %r)' % 
                            (s, all_signals))
                    raise BadConfig(msg, self, 'signals')
                self.signals.append(s)

        return self.signals

    def init(self):
        # let's do the rest of the initialization

        # signal -> table
        self.signal2table = {}
        # signal -> index in the table (or None)
        self.signal2index = {}

        for signal in self.signals:
            self.signal2table[signal] = self.log_group._f_getChild(signal)
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
            return (False, None)
        else:
            return (True, next_timestamp)

    def update(self):
        next_signal, next_timestamp = self._choose_next_signal()

        table = self.signal2table[next_signal]
        index = self.signal2index[next_signal]
        assert next_timestamp == table[index]['time']
        value = table[index]['value']

        self.set_output(next_signal, value=value, timestamp=next_timestamp)

        # update index
        if index + 1 == len(table):
            # finished
            self.signal2index[next_signal] = None
        else:
            self.signal2index[next_signal] = index + 1

        # write status message if not quiet
        if next_signal == self.signals[0] and not self.config.quiet:
            self.write_update_message(index, len(table), next_signal)

    def write_update_message(self, index, T, signal, nintervals=10):
        interval = int(numpy.floor(T * 1.0 / nintervals))
        if (index > 0 and
            index != interval * (nintervals) and
            index % interval == 0):
            percentage = index * 100.0 / T
            T = str(T)
            index = str(index).rjust(len(T))
            self.debug('%s read %.0f%% (%s/%s) (tracking signal %r).' % 
                        (self.config.file, percentage, index, T, signal))

    def finish(self):
        tc_close(self.hf)


