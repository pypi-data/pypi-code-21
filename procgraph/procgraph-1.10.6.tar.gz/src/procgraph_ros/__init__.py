''' 
    This is a set of blocks to read and write logs in ROS_ Bag format.
    
    You need the `rospy` package to be installed.
    
    .. _pytables: http://pytables.org
     
    .. _ROS: http://www.ros.org

'''

procgraph_info = {
    # List of python packages 
    'requires': ['ros', 'rosbag_utils']
}


# Smart dependency importing
from procgraph import import_magic, import_succesful, logger

rosbag = import_magic(__name__, 'ros', 'rosbag')
rosbag_utils = import_magic(__name__, 'rosbag_utils')

if import_succesful(rosbag_utils):
    from .bagread import BagRead
    from .bagwrite import BagWrite
    from .conversions import *
else:
    msg = 'Could not import rosbag_utils; install from git@github.com:AndreaCensi/ros_node_utils.git'
    logger.error(msg)

from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)
