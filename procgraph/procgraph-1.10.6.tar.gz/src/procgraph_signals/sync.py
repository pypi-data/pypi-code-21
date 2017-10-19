from collections import namedtuple
from procgraph import Block, ETERNITY, Generator


__all__ = [
    'Sync',
]


Sample = namedtuple('Sample', 'timestamp value')


class Sync(Generator):
    ''' 
    This block synchronizes a set of streams to the first stream (the master).
    
    The first signal is called the "master" signal.
    The other (N-1) are slaves.
    
    We guarantee that:
    
    - if the slaves are faster than the master,
      then we output exactly the same.
      
    Example diagrams: ::
      
        Master  *  *  *   *   *
        Slave   ++++++++++++++++
        
        Master  *  *  *   *   *
        output? v  v  x   v  
        Slave   +    +      +   
        output? v    v      v
    '''
    Block.alias('sync')

    Block.input_is_variable('Signals to synchronize. The first is the master.',
                             min=2)
    Block.output_is_variable('Synchronized signals.')

    def init(self):
        # output signals get the same name as the inputs
        names = self.get_input_signals_names()

        # create a state for each signal: it is an array
        # of tuples (timestamp, tuple)
        queues = {}
        for signal in names:
            queues[signal] = []

        # note in all queues, 
        # [(t0,...), (t1,...), ... , (tn,...) ]
        # and we have t0 > tn
        # The chronologically first (oldest) is queue[-1]
        # You get one out using queue.pop()
        # You insert one with queue.insert(0,...)

        self.set_state('queues', queues)
        self.state.already_seen = {}

        self.set_state('master', names[0])
        self.set_state('slaves', names[1:])

        # The output is an array of tuple (timestamp, values)
        # [
        #    (timestamp1, [value1,value2,value3,...]),
        #    (timestamp1, [value1,value2,value3,...])
        # ]#
        self.set_state('output', [])

    def update(self):
        def debug(s):
            if False:  # XXX: use facilities
                print('sync %s %s' % (self.name, s))

        output = self.get_state('output')
        queues = self.get_state('queues')
        names = self.get_input_signals_names()
        # for each input signal, put its value in the queues
        # if it is not already present
        for i, name in enumerate(names):
#            Commenting this; we clarified 0 = eternity; None = no signal yet
            if not self.input_signal_ready(i):    
                debug('Ignoring signal %r because timestamp is None.' % name)
                continue
            
            current_timestamp = self.get_input_timestamp(i)
            current_value = self.get_input(i)
            
            if  (name in self.state.already_seen and
                 self.state.already_seen[name] == current_timestamp):
                continue
            else:
                self.state.already_seen[name] = current_timestamp

            queue = queues[name]
            # if there is nothing in the queue
            # or this is a new sample
            if ((len(queue) == 0) or
                newest(queue).timestamp != current_timestamp):  # new sample
                debug("Inserting signal '%s'  ts %s (queue len: %d)" % 
                      (name, current_timestamp, len(queue)))
                # debug('Before the queue is: %s' % queue)
                add_last(queue, Sample(timestamp=current_timestamp,
                                       value=current_value))

                # debug('Now the queue is: %s' % queue)

        master = self.get_state('master')
        master_queue = queues[master]
        slaves = self.get_state('slaves')

        # if there is more than one value in each slave
        if len(master_queue) > 1:
            val = master_queue.pop()
            debug('DROPPING master (%s) ts =%s' % (master, val.timestamp))

        # Now check whether all slaves signals are >= the master
        # If so, output a synchronized sample.
        if master_queue:
            all_ready = True
            master_timestamp = master_queue[-1].timestamp
            # print "Master timestamp: %s" % (master_timestamp)
            for slave in slaves:
                slave_queue = queues[slave]
                # remove oldest
                while (len(slave_queue) > 1 and
                      oldest(slave_queue).timestamp < master_timestamp and
                      oldest(slave_queue).timestamp != ETERNITY):
                    debug("DROP one from %s" % slave)
                    slave_queue.pop()

                if not slave_queue:
                    # or (master_timestamp > slave_queue[-1].timestamp): 
                    all_ready = False
                    # its_ts = map(lambda x:x.timestamp, slave_queue)
                    # print "Slave %s not ready: %s" %(slave, its_ts)
                    break

            if all_ready:
                debug("**** Ready: master timestamp %s " % (master_timestamp))
                master_value = master_queue.pop().value
                output_values = [master_value]
                for slave in slaves:
                    # get the freshest still after the master
                    slave_queue = queues[slave]
                    slave_timestamp, slave_value = slave_queue.pop()
                    # print('Slave, %s %s ' % (slave, slave_timestamp))
                    if slave_timestamp == ETERNITY:
                        slave_queue.append((slave_timestamp, slave_value))
                    # # not true anymore, assert slave_timestamp >= 
                    # master_timestamp
                    # difference = slave_timestamp - master_timestamp
                    # debug(" - %s timestamp %s diff %s" % 
                    #      (slave, slave_timestamp, difference))
                    output_values.append(slave_value)
                output.insert(0, (master_timestamp, output_values))

        # XXX XXX not really sure here
        # if master has more than one sample, then drop the first one

        # if we have something to output, do it 
        if output:
            timestamp, values = output.pop()
            # FIXME: had to remove this for Vehicles simulation 
            # assert timestamp > 0
            debug("---------------- @ %s" % timestamp)
            for i in range(self.num_output_signals()):
                self.set_output(i, values[i], timestamp)

    def next_data_status(self):
        output = self.get_state('output')
        if not output:  # no output ready
            return (False, None)
        else:
            timestamp = self.output[-1][0]
            return (True, timestamp)


def oldest(queue):
    return queue[-1]


def newest(queue):
    return queue[0]


def add_last(queue, ob):
    queue.insert(0, ob)
