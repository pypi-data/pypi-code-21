from procgraph import Block
from procgraph.block_utils import make_sure_dir_exists
import os


PROCGRAPH_LOG_GROUP = 'procgraph'


class BagWrite(Block):
    ''' This block writes the incoming signals to a ROS bag file.
     
    By default, the signals are organized as follows: ::
    
         /            (root)
         /procgraph             (group with name procgraph)
         /procgraph/signal1     (table)
         /procgraph/signal2     (table)
         ...
   

    Note that the input should be ROS messages; no conversion is done.
    
    '''

    Block.alias('bagwrite')
    Block.input_is_variable('Signals to be written', min=1)
    Block.config('file', 'Bag file to write')

    def init(self):
        from ros import rosbag  # @UnresolvedImport

        self.info('Writing to bag %r.' % self.config.file)
        make_sure_dir_exists(self.config.file)

        if os.path.exists(self.config.file):
            os.unlink(self.config.file)
        self.tmp_file = self.config.file + '.active'
        self.bag = rosbag.Bag(self.tmp_file, 'w', compression='bz2')
        self.signal2last_timestamp = {}

    def finish(self):
        self.bag.close()
        os.rename(self.tmp_file, self.config.file)

    def update(self):
        import rospy 
        signals = self.get_input_signals_names()

        for signal in signals:
            msg = self.get_input(signal)
            timestamp = self.get_input_timestamp(signal)
            if ((signal in self.signal2last_timestamp) and
                (timestamp == self.signal2last_timestamp[signal])):
                continue
            self.signal2last_timestamp[signal] = timestamp

            ros_timestamp = rospy.Time.from_sec(timestamp)
            self.bag.write('/%s' % signal, msg, ros_timestamp)


