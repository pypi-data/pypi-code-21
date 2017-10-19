from itertools import tee, izip

from geometry import SE2, SE3, se3, linear_angular_from_se2
import numpy as np
from procgraph import Block


class SE2_relative_pose(Block):
    """ Lets the first pose be the identity """
    Block.input('pose')
    Block.output('rel_pose')
    
    def init(self):
        self.state.pose0 = None
    
    def update(self):
        pose = self.input.pose
        if self.state.pose0 is None:
            self.state.pose0 = pose
            
        rel_pose = SE2.multiply(SE2.inverse(self.state.pose0), pose)
        
        self.output.rel_pose = rel_pose
    

class se2_from_SE2_seq(Block):
    ''' Computes velocity in se2 given poses in SE2. '''
    Block.alias('se2_from_SE2_seq')

    Block.input('pose', 'Pose as an element of SE2',
                dtype=SE2)
    Block.output('velocity', 
                 'Velocity as an element of se(2).',
                 dtype=np.dtype(('float', (3, 3))))

    def init(self):
        self.state.prev = None

    def update(self):
        q2 = self.get_input(0)
        t2 = self.get_input_timestamp(0)

        if self.state.prev is not None:
            t1, q1 = self.state.prev
            vel = velocity_from_poses(t1, q1, t2, q2)
            self.set_output(0, vel, timestamp=t2)

        self.state.prev = t2, q2

class vel_from_SE2_seq(Block):
    ''' Computes velocity in se2 represented as vx,vy,omega
        from a sequence of poses in SE2. '''
    Block.alias('vel_from_SE2_seq')

    Block.input('pose', 'Pose as an element of SE2', dtype=SE2)
    Block.output('velocity', 'Velocity as vx,vy,omega.',
                 dtype=np.dtype(('float', 3)))

    def init(self):
        self.state.prev = None
    
    def update(self):
        q2 = self.get_input(0)
        t2 = self.get_input_timestamp(0)
        
        if self.state.prev is not None:
            t1, q1 = self.state.prev
            vel = velocity_from_poses(t1, q1, t2, q2, S=SE2)

            # Convertion from se2 to R3
            v, omega = linear_angular_from_se2(vel)
            out = np.array([v[0], v[1], omega])

            self.set_output(0, out, timestamp=t2)
            
        self.state.prev = t2, q2

class vel_from_SE3_seq(Block):
    ''' Computes velocity in se3 represented as vx,vy,vz,w1,w2,w3
        from a sequence of poses in SE3. '''
    Block.alias('vel_from_SE3_seq')

    Block.input('pose', 'Pose as an element of SE3', dtype=SE3)
    Block.output('velocity', 'Velocity as vx,vy,vz,w1,w2,w3',
                 dtype=np.dtype(('float', 6)))

    def init(self):
        self.state.prev = None

    def update(self):
        q2 = self.get_input(0)
        t2 = self.get_input_timestamp(0)

        if self.state.prev is not None:
            t1, q1 = self.state.prev
            vel = velocity_from_poses(t1, q1, t2, q2, S=SE3)
            out = se3.vector_from_algebra(vel)
            self.set_output(0, out, timestamp=t2)

        self.state.prev = t2, q2


def pose_difference(poses, S=SE2):
    """ poses: sequence of (timestamp, pose) """ 
    
    for p1, p2 in pairwise(poses):
        t1, q1 = p1
        t2, q2 = p2
        v = velocity_from_poses(t1, q1, t2, q2, S=S)
        yield v

def velocity_from_poses(t1, q1, t2, q2, S=SE2):
    delta = t2 - t1
    if not delta > 0:
        raise ValueError('invalid sequence')

    x = S.multiply(S.inverse(q1), q2)
    xt = S.algebra_from_group(x)
    v = xt / delta
    return v

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

# 
# class MyInput(object):
#     def __init__(self, block):
#         self.block = block
#         
#         
# class SimpleSequenceBlock(IteratorGenerator):
# 
#     def init_iterator(self):
#         my_input = MyInput(self)
#         myit = self.get_iterator(my_input)
#         
#         def add_signal_name(it):
#             for timestamp, value in it:
#                 yield timestamp, 0, value
#         
#         return add_signal_name(myit)
# 
#     @abstractmethod
#     @contract(returns=GeneratorType)
#     def get_iterator(self, input_sequence):
#         pass
# 
#     def init(self):
#         self.iterator = self.init_iterator()
#         if self.iterator is None:
#             msg = 'must return an iterator, got %s' % describe_value(self.iterator)
#             raise ValueError(msg)
#         self._load_next()
# 
#     def _load_next(self):
#         try:
#             signal, timestamp, value = self.iterator.next()
#             if not isinstance(signal, (str, int)):
#                 msg = ('Expected a string or number for the signal, got %s' % 
#                        describe_value(signal))
#                 raise ValueError(msg)
#             if not isinstance(timestamp, float):
#                 msg = ('Expected a number for the timestamp, got %s' % 
#                        describe_value(timestamp))
#                 raise ValueError(msg)
#             
#             self.next_signal = signal
#             self.next_timestamp = timestamp
#             self.next_value = value
#             self.has_next = True
#         except StopIteration:
#             self.has_next = False
# 
#     def next_data_status(self):
#         if self.has_next:
#             return (True, self.next_timestamp)
#         else:
#             return (False, None)
# 
#     def update(self):
#         if not self.has_next:
#             return  # XXX: error here?
# 
#         self.set_output(self.next_signal,
#                         value=self.next_value, timestamp=self.next_timestamp)
# 
#         self._load_next() 
#         
#         
# class VelocityFromPoses(SimpleSequenceBlock):
#     
#     Block.input('pose', 'Pose as an element of SE2')
#     
#     def get_iterator(self, input_sequence):
#         for t, x in pose_difference(input_sequence):
#             yield t, x
#     
#          
