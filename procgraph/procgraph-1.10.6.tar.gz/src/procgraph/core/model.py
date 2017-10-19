from ..utils import indent
from .block import Block, Generator
from .constants import ETERNITY, STRICT_CHECK_OF_DEFINED_IO
from .exceptions import (BadMethodCall, ModelExecutionError, ModelWriterError,
    SemanticError)
from .model_io import ModelInput, ModelOutput
from .model_stats import ExecutionStats, write_stats
from .visualization import debug as debug_main, info, warning
import time
import warnings


__all__ = ['Model'] 


class Model(Generator):
    ''' 
        A Model is a block and a generator. 
    
    
        cleanup() and finish(): "cleanup" is the emergency clean up.
        It is called after finish().
        
        Order in which init(), update(), cleanup() can be called:
        - init(), update(), ..., update(), finish(), cleanup() 
        - init(), finish(), cleanup()
        - init(), cleanup()
        
    '''

    def __init__(self, name, model_name):
        ''' Name is the personal name of this instance.
            model_name is this model's name.
            
            model_name is used for visualization and serialization
            config is usef only for serialization.
             '''
        if name is None:
            name = 'unnamed-block'
        assert isinstance(name, str)

        if model_name is None:
            model_name = 'unnamed-model'
        assert isinstance(model_name, str)

        self.model_name = model_name

        # As a block
        Block.__init__(self, name=name, config={}, library=None)

        self.name2block = {}
        self.name2block_connection = {}
        # block -> block unresolved 
        self.unresolved = {}

        # list of blocks that act as generators (instance of Generator)
        self.generators = []

        self.reset_execution()

        # dict signal name -> Block for blocks of type ModelInput
        self.model_input_ports = {}
        # dict signal name -> Block for blocks of type ModelInput
        self.model_output_ports = {}

        self.stats = ExecutionStats()

        self._already_inited = False

        self.level = 0

    def add_block(self, name, block):
        '''  Add a block to the model. Returns the block instance. '''
        assert not name in self.name2block, 'Name %r already taken' % name

        self.name2block[name] = block

        if isinstance(block, Generator):
            self.generators.append(block)

        if isinstance(block, ModelInput):
            block.init()  # get the name from config
            if not self.is_valid_input_name(block.signal_name):
                msg = 'Input %r was not defined formally.' % block.signal_name
                if STRICT_CHECK_OF_DEFINED_IO:
                    raise SemanticError(msg, block)
                else:
                    warning("Warning: %s" % msg)

                if self.are_input_signals_defined():
                    all_inputs = self.get_input_signals_names()
                else:
                    all_inputs = []

                self.define_input_signals_new(all_inputs + [block.signal_name])

            self.model_input_ports[block.signal_name] = block

        if isinstance(block, ModelOutput):
            block.init()  # get the name from config

            if not self.is_valid_output_name(block.signal_name):
                msg = 'Output %r was not defined formally.' % block.signal_name
                if STRICT_CHECK_OF_DEFINED_IO:
                    raise SemanticError(msg, block)
                else:
                    warning("Warning: %s" % msg)

                if self.are_output_signals_defined():
                    all_outputs = self.get_output_signals_names()
                else:
                    all_outputs = []

                # XXX: bug: output_signals -> output_signals
                self.define_output_signals_new(all_outputs + 
                                               [block.signal_name])

            self.model_output_ports[block.signal_name] = block

        return block

    def from_outside_set_input(self, num_or_id, value, timestamp):
        assert self._already_inited, 'The block must first be init()ed.'
        Block.from_outside_set_input(self, num_or_id, value, timestamp)

        signal_name = self.canonicalize_input(num_or_id)
        input_block = self.model_input_ports[signal_name]
        input_block.set_output(signal_name, value, timestamp)
        self.blocks_to_update.append(input_block)

    def connect(self,
                block1, block1_signal,
                block2, block2_signal,
                public_name):
        ''' Caller should check that the public name is not taken. '''
        assert public_name is not None
        if public_name in self.public_signal_names():
            msg = ('The name %r is already present in:\n' % public_name)
            for s in self.public_signal_names():
                msg += '- %s\n' % s
            raise ValueError(msg)
            

        BC = BlockConnection(block1, block1_signal, block2, block2_signal,
                             public_name)

        self.name2block_connection[public_name] = BC

    def public_signal_names(self):
        ''' Returns the set of public signal names. '''
        return set(self.name2block_connection.keys())

    def next_data_status(self):
        ''' XXX: OK, I'm writing this late and probably it's more 
            complicated than this. '''
        generator_timestamps = []
        at_least_one = False
        for generator in self.generators:
            status = generator.next_data_status()
            (has_next, timestamp) = status  # @UnusedVariable
            if has_next:
                at_least_one = True
                if timestamp is not None:
                    generator_timestamps.append(timestamp)
                else:
                    pass
#                    self.debug('No timestamp for %s' % generator)

        if not at_least_one:
            return (False, None)
        elif not generator_timestamps:
            return (True, None)
        else:
            return (True, min(generator_timestamps))

    def has_more(self):
        """ Returns true if there are blocks with pending updates,
            or there is at least one generator that has not ended. """
        if self.blocks_to_update:
            return True

        for generator in self.generators:
            # print('checking %s' % generator)
            status = generator.next_data_status()  # @UnusedVariable

            if not isinstance(status, tuple) or len(status) != 2:
                msg = ('next_data_status() should return a tuple of len 2, '
                       ' not %r.' % status)
                raise ModelWriterError(msg, generator)
            (has_next, timestamp) = status  # @UnusedVariable
            if has_next:
                return True

        return False

    def reset_execution(self):
        self.blocks_to_update = []
        # add all the blocks without input to the update list
        for block in self.name2block.values():
            if isinstance(block, Model):
                # Don't consider generators because has_more() will consider 
                # them.
                # This is mainly for propagating constants.
                if block.blocks_to_update:
                    self.blocks_to_update.append(block)
                pass
            elif (not isinstance(block, ModelInput) and
                 not isinstance(block, Generator) and
                 block.num_input_signals() == 0):
                # These are the constants blocks.
                self.blocks_to_update.append(block)

    def init(self):
        assert not self._already_inited, 'The block has already been init()ed.'
        self._already_inited = True
        for block in self.name2block.values():
            block.level = self.level + 1
            block.init()
        self.reset_execution()

    def finish(self):
        for block in self.name2block.values():
            try:
                block.finish()
            except Exception as e:
                raise BadMethodCall('finish', block, e)
            except BadMethodCall as e:
                e.blocks.insert(0, block)
                raise e

    def cleanup(self):
        ''' We try hard to call cleanup() on all the blocks. '''
        blocks_failed = []
        msg = ""
        for block in self.name2block.values():
            try:
                block.cleanup()
            except Exception as e:
                msg += ('Cleanup for %s failed:\n%s\n' % 
                        (block, indent(e, '> ')))
                blocks_failed.append(block)
                
        if blocks_failed:
            s = ('Cleanup for %d blocks failed.\n%s' % 
                 (len(blocks_failed), msg))
            raise Exception(s)  # XXX: which other exception?

    def update(self):
        do_stats = True

        if do_stats:
            warnings.warn('Performance much reduced due to stats.')

        # Turn on debugging here
        def debug(s):
            if False:
                debug_main('Model %s | %s' % (self.model_name, s))

        # We keep a list of blocks to be updated.
        # If the list is not empty, then pop one and update it.
        if self.blocks_to_update:
            # get one block
            block = self.blocks_to_update.pop(0)

            debug('Got block to update %s' % block)

        else:
            debug('No blocks to update')

            # look if we have any generators
            # list of (generator, timestamp) 
            generators_with_timestamps = []
            for generator in self.generators:
                (has_next, timestamp) = generator.next_data_status()
                if has_next:
                    generators_with_timestamps.append((generator, timestamp))

            if not generators_with_timestamps:
                msg = "You asked me to update but nothing's left."
                raise ModelExecutionError(msg, self)

            # now look for the smallest available timestamp
            # (timestamp can be none)
            def cmpk(timestamp1, timestamp2):
                if timestamp1 is None:
                    return 1
                elif timestamp2 is None:
                    return -1
                elif timestamp1 < timestamp2:
                    return -1
                elif timestamp2 < timestamp1:
                    return 1
                else:
                    return 0

            generators_with_timestamps.sort(key=lambda x: x[1], cmp=cmpk)
            block = generators_with_timestamps[0][0]

        if block is None:
            # We finished everything
            msg = "You asked me to update but nothing's left."
            raise ModelExecutionError(msg, self)

        # now we have a block (could be a generator)
#        debug('Updating %s (input ts: %s)' %
#              (block, block.get_input_signals_timestamps()))

        # We also time the execution
        start_cpu = time.clock()
        start_wall = time.time()

        try:
            result = block.update()
        except BadMethodCall as e:
            e.blocks.insert(0, block)
            raise e
        except Exception as e:
            raise BadMethodCall('update', block, e)

        if block.get_input_signals_timestamps():
            timestamp = max(block.get_input_signals_timestamps())
        elif block.get_output_signals_timestamps():
            timestamp = max(block.get_output_signals_timestamps())
        else:  # for those that don't have input signals
            timestamp = ETERNITY

        if do_stats:
            wall = time.time() - start_wall
            stop_cpu = time.clock()
            cpu = stop_cpu - start_cpu
            if cpu == 0:
                print('Low resolution clock() - start: %s stop: %s wall: %s - using wall time.' % (start_cpu, stop_cpu, wall))
                cpu = wall
                # raise ValueError('No CPU? wall = %s' % wall)

            # print('block: %s cpu: %s time: %s of %s' % (block, cpu, timestamp, block.get_output_signals_timestamps()))
            self.stats.add(block=block, cpu=cpu, wall=wall, timestamp=timestamp)

        # if the update is not finished, we put it back in the queue
        if result == block.UPDATE_NOT_FINISHED:
            self.blocks_to_update.insert(0, block)
        else:
            # the block updated, propagate
            # debug("  processed %s, ts: %s" % (block, block.get_output_signals_timestamps()))
            # debug("  its successors: %s" % list(self.__get_output_connections(block)))

            # check if the output signals were updated
            for connection in self.__get_output_connections(block):
                other = connection.block2
                # debug("  - considering connection %s to %s" % (connection, other))
                # Don't include dummy connection
                if other is None:
                    # debug("   ignoring dummy connection %s" % connection)
                    continue
                other_signal = connection.block2_signal
                
                this_signal = connection.block1_signal
                this_timestamp = block.get_output_timestamp(this_signal)

                value = block.get_output(this_signal)

                if value is not None and this_timestamp is None:
                    msg = ('Strange, value is not None but the timestamp is 0'
                          ' for output signal %r of block %s.' % 
                            (block.canonicalize_output(this_signal), block))
                    raise ModelExecutionError(msg, block)

                # Ignore if this signal wasn't updated yet
                if this_timestamp is None:
                    # debug("   ignoring because timestamp is None")
                    continue
                
                to_update = ((not other.input_signal_ready(other_signal)) or
                             (this_timestamp > other.get_input_timestamp(other_signal))) 
                
                if to_update:
                    # debug('  then waking up %s' % other)

                    other.from_outside_set_input(other_signal, value,
                                                 this_timestamp)

                    if not other in self.blocks_to_update:
                        self.blocks_to_update.append(other)

                    if do_stats:
                        self.stats.add_connection_sample(connection=connection,
                                                 value=value,
                                                 timestamp=this_timestamp)


                    # If this is an output port, update the model
                    if isinstance(other, ModelOutput):
                        self.set_output(other.signal_name,
                                        value, this_timestamp)
                else:
                    # debug("   not updated %s because not %s > %s." %
                    #       (other, this_timestamp, other.get_input_timestamp(other_signal)))
                    pass

        # now let's see if we have still work to do
        # this step is important when the model is inside another one
        if self.blocks_to_update:
            return Block.UPDATE_NOT_FINISHED
        else:
            return True

    def __get_output_connections(self, block):
        for block_connection in self.name2block_connection.values():
            if block_connection.block1 == block:
                yield block_connection

    def __get_successors(self, block):
        ''' Returns an iterable of all the blocks connected
            to one of the outputs of the given block. '''
        successors = set()
        for block_connection in self.name2block_connection.values():
            if block_connection.block1 == block:
                successors.add(block_connection.block2)
        return successors

    def __repr__(self):
        s = 'M:%s:%s(' % (self.model_name, self.name)
        s += self.get_io_repr()
        s += ')'
        return s

    def summary(self):
        info("--- Model: %d blocks, %d connections" % 
            (len(self.name2block), len(self.name2block_connection)))
        for name, block in self.name2block.items():
            info("- %s: %s" % (name, block))

        for name, conn in self.name2block_connection.items():
            info("- %s: %s" % (name, conn))

    def print_stats(self):
        """ Prints statistics for the leaves of the hierarchy. """
        all_samples = self.collect_stats_leaves()
        write_stats(all_samples)

    def collect_stats_leaves(self):
        """ Collects the stats from the leaves. """
        all_samples = []
        for block in self.name2block.values():
            if isinstance(block, Model):
                all_samples.extend(block.collect_stats_leaves())

        leaves = [v for (b, v) in self.stats.samples.items()
                  if not isinstance(b, Model)]
        all_samples.extend(leaves)
        return all_samples

    def stats_get_all(self):
        """ Returns a structure for all stats recursively. """
        s = self.stats.get_all()
        for block in self.name2block.values():
            if isinstance(block, Model):
                block_stats = block.stats_get_all()
                block_blocks = block_stats['blocks']
                for bname, x in block_blocks.items():
                    s['blocks']['%s.%s' % (block.name, bname)] = x

                block_signals = block_stats['signals']
                for signal in block_signals:
                    s2 = signal.copy()
                    s2['block1'] = '%s.%s' % (block.name, s2['block1'])

                    s2['block2'] = '%s.%s' % (block.name, s2['block2'])
                    s['signals'].append(s2)

        return s


class BlockConnection(object):
    def __init__(self, block1, block1_signal, block2, block2_signal,
                       public_name=None):
        assert isinstance(block1, Block)
        assert block1_signal is not None
        assert block2 is None or isinstance(block2, Block)

        self.block1 = block1
        self.block1_signal = block1_signal
        self.block2 = block2
        self.block2_signal = block2_signal
        self.public_name = public_name

    def __repr__(self):
        s = 'Connection('
        s += self.block1.name
        s += '.%s' % self.block1_signal

        s += ' --> '
        if self.block2:
            s += self.block2.name
            s += '.%s' % self.block2_signal
        else:
            s += '?.?'
        s += ')'

        return s
