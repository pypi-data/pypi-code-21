from contracts import contract
from procgraph import BadConfig, Block, Generator
from rosbag_utils import resolve_topics, rosbag_info_cached
import warnings
from pprint import pformat


__all__ = ['BagRead']

class BagRead(Generator):
    ''' 
        This block reads a bag file (ROS logging format).
    '''
    Block.alias('bagread')
    Block.output_is_defined_at_runtime('The signals read from the log.')
    Block.config('file', 'Bag file to read')
    Block.config('limit', 'Limit in seconds on how much data we want. (0=no limit)', 
                            default=0)
    Block.config('topics', 'Which signals to output (and in what order). '
                 'Should be a comma-separated list. If you do not specify it '
                 '(or if empty) it will be all signals.',
                 default=[])
 
    Block.config('quiet', 'If true, disables advancements status messages.',
                 default=False)
      
              
    @contract(returns='list(str)')
    def get_topics(self):
        bagfile = self.config.file
        if self.config.topics is not None:
            given_topics = self.config.topics.strip()
        else:
            given_topics = None
  
        if given_topics:
            topics = given_topics.split(',')
        else:
            all_topics = [c.topic for c in self.bag._get_connections()]
            topics = sorted(set(all_topics))

        self.baginfo = rosbag_info_cached(bagfile)
        res, _, asked2resolved = resolve_topics(self.baginfo, topics)
        self.info('Resolving:\n%s' % pformat(asked2resolved))
        return res
    
    def get_output_signals(self):
        import rosbag 
        self.bag = rosbag.Bag(self.config.file)
        
        self.topics = self.get_topics()

        self.topic2signal = {}
        signals = []
        for t in self.topics:
            self.info(t)
            if ':' in t:
                tokens = t.split(':')
                assert len(tokens) == 2
                t = tokens[0]
                signal_name = tokens[1]
            else:
                signal_name = str(t).split('/')[-1]
            if signal_name in signals:
                self.error('Warning: repeated name %s' % signal_name)
                signal_name = ("%s" % t).replace('/', '_')
                self.error('Using long form %r.' % signal_name)
            signals.append(signal_name)
            self.topic2signal[t] = signal_name

        topics = self.topic2signal.keys()

        self.info(self.topic2signal)

        limit = self.config.limit
        if not isinstance(limit, (float, int)):
            msg = 'I require a number; 0 for none.'
            raise BadConfig(msg, self, 'limit')

        start_time, end_time = self._get_start_end_time(limit)
        params = dict(topics=topics, start_time=start_time, end_time=end_time)
        self.iterator = self.bag.read_messages(**params)

        return signals
    
    @contract(limit='None|number')
    def _get_start_end_time(self, limit):
        """ 
            Returns the start and end time to use (rospy.Time).
        
            also sets self.start_stamp, self.end_stamp
            
        """
        from rospy.rostime import Time  # @UnresolvedImport
        self.info('limit: %r' % limit)
        warnings.warn('Make better code for dealing with unindexed')
        if limit is not None and limit != 0:
            # try:
            chunks = self.bag.__dict__['_chunks']
            self.start_stamp = chunks[0].start_time.to_sec()
            self.end_stamp = chunks[-1].end_time.to_sec()
            start_time = Time.from_sec(self.start_stamp)
            end_time = Time.from_sec(self.start_stamp + limit)
            return start_time, end_time
            # except Exception as e:
            #     self.error('Perhaps unindexed bag?')
            #     self.error(traceback.format_exc(e))
            #     raise
            #     start_time = None
            #     end_time = None
            #      
            # self.info('start_stamp: %s' % self.start_stamp)
            # self.info('end_stamp: %s' % self.end_stamp)
        else:
            self.start_stamp = None
            self.end_stamp = None
            return None, None
                

    def init(self):
        self._load_next()

    def _load_next(self):
        try:
            topic, msg, timestamp = self.iterator.next()
            self.next_timestamp = timestamp.to_sec()
            self.next_value = msg
            self.next_topic = topic
            self.next_signal = self.topic2signal[topic]
            self.has_next = True
        except StopIteration:
            self.has_next = False

    def next_data_status(self):
        if self.has_next:
            return (self.next_signal, self.next_timestamp)
        else:
            return (False, None)

    def update(self):
        if not self.has_next:
            return  # XXX: error here?

        self.set_output(self.next_signal,
                        value=self.next_value,
                        timestamp=self.next_timestamp)

        self._load_next()

    def finish(self):
        self.bag.close()


