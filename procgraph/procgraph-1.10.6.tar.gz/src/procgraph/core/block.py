from contracts import contract, new_contract

from .block_config import resolve_config
from .block_meta import BlockMeta, BlockMetaSugar
from .block_sugar import InputProxy, OutputProxy, StateProxy, ConfigProxy
from .exceptions import BlockWriterError, ModelWriterError, ModelExecutionError


__all__ = [
    'Block',
    'NOT_READY',
    'Generator',
]


NOT_READY = None

new_contract('num_or_id', 'int|str')

class Block(BlockMetaSugar):
    __metaclass__ = BlockMeta

    def __init__(self, name, config, library):  # @UnusedVariable
        assert isinstance(name, str), \
            'The block name must be a string, not %s' % name.__class__

        self.name = name

        list_of_config = self.__class__.config
        self.__config = resolve_config(list_of_config, config, None)

        # this is an array containing the names/ids
        # example: ["y", 1, 2]
        self.__input_signal_names = None
        # example: {"y":0, "1":1, "2":2}
        self.__input_signal_name2id = None
        # this is an array of Values
        self.__input_signals = None

        # same as above
        self.__output_signal_names = None
        self.__output_signal_name2id = None
        self.__output_signals = None

        # state variables
        self.__states = {}

        # instantiation point
        self.where = None

        # proxies for accessing input, output, and state
        self.input = InputProxy(self)
        self.output = OutputProxy(self)
        self.state = StateProxy(self)
        self.config = ConfigProxy(self)

        # used for debug; hierarchical level
        self.level = 0
        
        # used for info_once() and error_once(): messages we already sent
        self._msgs_written = set()
        # Used by input_update_available()
        self._input_update_available_last = {}

    def init(self):
        ''' Initializes the block.  '''
        pass

    def update(self):
        ''' Performs the block function. '''
        pass

    def finish(self):
        pass

    def cleanup(self):
        pass

    # TODO: move away
    UPDATE_NOT_FINISHED = 'update-not-finished'

    # Used during initialization
    def num_input_signals(self):
        assert self.are_input_signals_defined(), \
            'No input defined for %s' % self
        return len(self.__input_signals)

    def num_output_signals(self):
        assert self.are_output_signals_defined(), \
            'No output defined for %s' % self
        return len(self.__output_signals)

    def get_input_signals_names(self):
        ''' Returns the list of names of currently defined input signals. '''
        assert self.are_input_signals_defined(), \
            'No input defined for %s' % self
        return list(self.__input_signal_names)

    def get_output_signals_names(self):
        ''' Returns the list of names of currently defined output signals. '''
        assert self.are_output_signals_defined(), \
            'No output defined for %s' % self
        return list(self.__output_signal_names)

    def are_input_signals_defined(self):
        return self.__input_signals is not None

    def are_output_signals_defined(self):
        return self.__output_signals is not None

    def define_input_signals_new(self, signals):
        if not isinstance(signals, list):
            msg = ('I expect the parameter to define_input_signals() to be a '
                    'list, instead got a %s: %s' % 
                    (signals.__class__.__name__, signals))
            raise BlockWriterError(msg)
        
        # Make sure unique
        if len(set(signals)) != len(signals):
            msg = 'Not unique set of signals names: %s' % signals
            raise BlockWriterError(msg)

        # reset structures
        self.__input_signal_names = []
        self.__input_signals = []
        self.__input_signal_name2id = {}
        for i, s in enumerate(signals):
            if not isinstance(s, str):
                msg = 'Invalid list of names for input: %s ' % signals
                raise BlockWriterError(msg)

            self.__input_signal_names.append(str(s))
            self.__input_signal_name2id[str(s)] = i
            self.__input_signals.append(Value(None, NOT_READY))

    @contract(returns='bool')
    def all_input_signals_ready(self):
        ''' Returns True if all input signals are ready. '''
        for value in self.__input_signals:
            if value.timestamp == NOT_READY:
                return False
        return True
    
#     @contract(signal='num_or_id', returns='bool')
    def input_signal_ready(self, signal):
        """ 
            Return True if the signal is ready, meaning that we have
            at least one value. 
        """
        res = bool(self.__get_input_struct(signal).timestamp != NOT_READY)
        # print('ready? %s %s' % (signal, res))
        return res


    @contract(signal='num_or_id', returns='bool')
    def input_update_available(self, signal):
        """ 
            Return True if the signal was updated since the last
            time this function was called with the same argument.
            
            Returns False if it's not ready.
        """
        
        if not self.input_signal_ready(signal):
            return False
        current = self.get_input_timestamp(signal)
        track = self._input_update_available_last
        
        if not signal in track:
            track[signal] = current 
            return True
        
        last_seen = track[signal]
        
        update_available = last_seen != current
        
        track[signal] = current
        
        return bool(update_available) 
          
    def define_output_signals_new(self, signals):
        if not isinstance(signals, list):
            msg = ('I expect the parameter to define_output_signals()' + 
                   ' to be a list, got a %s: %s' % 
                   (signals.__class__.__name__, signals))
            raise BlockWriterError(msg)

        # reset structures
        self.__output_signal_names = []
        self.__output_signals = []
        self.__output_signal_name2id = {}
        for i, s in enumerate(signals):
            if not isinstance(s, str):
                msg = ('Invalid list of names for output: %s; '
                        ' I expect strings.' % signals)
                raise BlockWriterError(msg)

            self.__output_signal_names.append(str(s))
            self.__output_signal_name2id[str(s)] = i
            self.__output_signals.append(Value(None, NOT_READY))

    def get_config(self, conf):
        if not conf in self.__config:
            msg = ('For block %s: could not find parameter %r in config %s.' % 
                   (self, conf, self.__config))
            raise ModelExecutionError(msg, self)

        return self.__config[conf]

    def set_state(self, varname, value):
        ''' Can be called during init() and update(). '''
        # TODO: add check and exception
        self.__states[varname] = value

    def get_state(self, varname):
        ''' Can be called during init() and update() .'''
        if not varname in self.__states:
            raise ValueError('No such state variable %r' % varname)
        return self.__states[varname]

    def get_state_vars(self):
        ''' Returns a list of the names for the state variables. '''
        # TODO: remove this?
        return list(self.__state.keys())

    # Functions that can be called during runtime
    def set_output(self, num_or_id, value, timestamp=None):
        ''' Sets an output value. If timestamp is omitted, it
            will default to the maximum of the input signals timestamp. '''
        if timestamp is None:
            if len(self.__input_signals) == 0:
                msg = ('%s: setting %s: timestamp not specified and no inputs'
                       % (self, num_or_id))
                raise Exception(msg)

            timestamp = max(self.get_input_signals_timestamps())

        output_struct = self.__get_output_struct(num_or_id)
        output_struct.value = value
        output_struct.timestamp = timestamp

    def from_outside_set_input(self, num_or_id, value, timestamp):
        ''' Sets an input value. This is used from outside, not 
        from the block. (This is overloaded by Model) '''
        if timestamp is None:
            msg = ('Setting input %r to %s with None timestamp' % 
                   (num_or_id, timestamp))
            raise ValueError(msg)
        input_struct = self.__get_input_struct(num_or_id)
        input_struct.value = value
        input_struct.timestamp = timestamp


    @contract(returns='tuple(float, *)')
    def get_input_ts_and_value(self, num_or_id):
        ''' Gets the timestamp and value of an input signal. '''
        if not self.input_signal_ready(num_or_id):
            msg = 'Cannot get_input_ts_and_value(%r): input not ready.' % num_or_id
            raise ValueError(msg)

        input_struct = self.__get_input_struct(num_or_id)
        value = input_struct.value
        ts = input_struct.timestamp
        return ts, value
        
    @contract(num_or_id='num_or_id')
    def get_input(self, num_or_id):
        ''' Gets the value of an input signal. '''
        if not self.input_signal_ready(num_or_id):
            msg = 'Cannot get_input(%r): input not ready.' % num_or_id
            raise ValueError(msg)

        input_struct = self.__get_input_struct(num_or_id)
        return input_struct.value

    @contract(num_or_id='num_or_id')
    def get_input_timestamp(self, num_or_id):
        ''' 
            Gets the timestamp of an input signal (None if it 
            has never been received).
        '''
        if not self.input_signal_ready(num_or_id):
            msg = 'Cannot get_input_timestamp(%r): input not ready.' % num_or_id
            raise ValueError(msg)
        input_struct = self.__get_input_struct(num_or_id)
        return input_struct.timestamp

    @contract(num_or_id='num_or_id')
    def get_output_timestamp(self, num_or_id):
        ''' Gets the timestamp of an output signal. '''
        output_struct = self.__get_output_struct(num_or_id)
        return output_struct.timestamp

    @contract(num_or_id='num_or_id')
    def get_output(self, num_or_id):
        ''' Gets the value of an output signal. '''
        output_struct = self.__get_output_struct(num_or_id)
        return output_struct.value

    @contract(num_or_id='num_or_id')
    def __get_input_struct(self, num_or_id):
        ''' Returns a reference to the Value structure of the given 
            input signal. 
        '''
        if not self.is_valid_input_name(num_or_id):
            msg = 'Unknown input name %r.' % str(num_or_id)
            raise ModelWriterError(msg, self)

        if isinstance(num_or_id, str):
            # convert from name to number 
            num_or_id = self.__input_signal_name2id[num_or_id]
        return self.__input_signals[num_or_id]

    @contract(num_or_id='num_or_id')
    def __get_output_struct(self, num_or_id):
        ''' Returns a reference to the Value structure of the given 
            output signal. 
        '''
        if not self.is_valid_output_name(num_or_id):
            msg = 'Unknown output name %r.' % str(num_or_id)
            raise ModelWriterError(msg, self)

        if isinstance(num_or_id, str):
            # convert from name to number
            num_or_id = self.__output_signal_name2id[num_or_id]
        return self.__output_signals[num_or_id]

    @contract(num_or_id='num_or_id')
    def is_valid_input_name(self, num_or_id):
        ''' Checks that num_or_id (string or int) is a valid handle
            for one of the signals. '''
        assert self.are_input_signals_defined(), \
            'No input defined for %s (checking %r)' % (self, num_or_id)

        if isinstance(num_or_id, str):
            return num_or_id in self.__input_signal_name2id
        if isinstance(num_or_id, type(0)):
            return num_or_id < len(self.__input_signals)
        raise ValueError('Invalid input name %r' % num_or_id)

    @contract(num_or_id='num_or_id')
    def canonicalize_input(self, num_or_id):
        ''' Converts the signal spec (either string or id) to string
            (useful because more user-friendly). '''
        assert self.is_valid_input_name(num_or_id), \
            '%r is not a valid input name.' % (self, num_or_id)
        if isinstance(num_or_id, str):
            return num_or_id
        if isinstance(num_or_id, type(0)):
            return self.__input_signal_names[num_or_id]
        raise ValueError('Invalid input name %r' % num_or_id)

    @contract(num_or_id='num_or_id')
    def is_valid_output_name(self, num_or_id):
        ''' Checks that num_or_id (string or int) is a valid handle
            for one of the signals. '''
        assert self.are_output_signals_defined(), \
            'No output defined for %s (checking %r)' % (self, num_or_id)

        if isinstance(num_or_id, str):
            return num_or_id in self.__output_signal_name2id
        if isinstance(num_or_id, type(0)):
            return num_or_id < len(self.__output_signals)

        raise ValueError('Invalid output type %r' % num_or_id)

    @contract(num_or_id='num_or_id')
    def canonicalize_output(self, num_or_id):
        ''' Converts the signal spec (either string or id) to string
            (useful because more user-friendly). '''
        assert self.is_valid_output_name(num_or_id), \
            '%r is not a valid output name.' % (self, num_or_id)
        if isinstance(num_or_id, str):
            return num_or_id
        if isinstance(num_or_id, type(0)):
            return self.__output_signal_names[num_or_id]
        raise ValueError('Invalid output name %r' % num_or_id)

    def get_output_signals_timestamps(self):
        ''' Returns a list of the output values timestamps. '''
        return [x.timestamp for x in self.__output_signals]

    def get_input_signals_timestamps(self):
        ''' Returns a list of the input signals timestamps. '''
        return [x.timestamp for x in self.__input_signals]

    def get_input_signals_values(self):
        ''' Returns a list of the input signals values. '''
        return [x.value for x in self.__input_signals]

    def __repr__(self):
        s = 'B:%s:%s(' % (self.__class__.__name__, self.name)
        s += self.get_io_repr()
        s += ')'
        return s

    def get_io_repr(self):
        ''' Returns a representation of io ports for this block. '''
        s = ""
        if self.are_input_signals_defined():
            if self.__input_signals:
                s += "in:%s" % ",".join(self.__input_signal_names)
            else:
                s += 'in:/'
        else:
            s += "in:?"

        s += ';'
        if self.are_output_signals_defined():
            if self.__output_signals:
                s += "out:%s" % ",".join(self.__output_signal_names)
            else:
                s += 'out:/'
        else:
            s += "out:?"
        return s

    def _log_prefix(self):
        return '%s%s:' % ('>' * self.level, self.name)


    def info_once(self, msg):
        if not msg in self._msgs_written:
            self.info(msg)
            self._msgs_written.add(msg)

    def error_once(self, msg):
        if not msg in self._msgs_written:
            self.error(msg)
            self._msgs_written.add(msg)

    def info(self, s):
        ''' Writes an info message. '''
        from .visualization import info as pg_info
        pg_info("%s%s" % (self._log_prefix(), s))

    def warning(self, s):
        ''' Writes an info message. '''
        from .visualization import warning as pg_warning
        pg_warning("%s%s" % (self._log_prefix(), s))

    def debug(self, s):
        ''' Writes a debug message. '''
        from .visualization import debug as pg_debug
        pg_debug("%s%s" % (self._log_prefix(), s))

    def error(self, s):
        ''' Writes a debug message. '''
        from .visualization import error as pg_error
        pg_error("%s%s" % (self._log_prefix(), s))


class Generator(Block):
    # TODO: change interface

    def next_data_status(self):
        ''' 
        This is complicated but necessary. Do you have another value?
        
        - Yes, and it will be of this timestamp. (I can see it from the log)
        
        - No, this generator has finished.
        
        - Yes, but this is realtime and it does not depend on me.
          For example, I'm waiting for the next sensor data. 
          Ask me later. 
          
        In those cases, we return:
        
            (True, timestamp)
            
            (False, None)
            
            (True, None)
          
        '''
        raise NotImplementedError('"next_data_status" was not implement.')



class Value(object):
    '''
        timestamp = ETERNITY     constant
        timestamp = NOT_READY = (None)         signal not ready 
    '''
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

