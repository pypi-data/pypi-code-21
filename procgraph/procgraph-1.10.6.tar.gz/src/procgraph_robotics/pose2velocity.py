from procgraph import Block, BadInput, register_model_spec

from . import geometry

g = geometry


class Pose2velocity(Block):
    ''' Block used by :ref:`block:pose2commands`. '''
    Block.alias('pose2vel_')

    Block.input('q12', 'Last two poses.')
    Block.input('t12', 'Last two timestamps.')

    Block.output('commands', 'Estimated commands ``[vx,vy,omega]``.')

    def update(self):
        q = self.get_input('q12')
        t = self.get_input('t12')
        if not (len(q) == 2 and len(t) == 2):
            raise BadInput('Bad input received.', self)

        pose1 = g.SE2_from_xytheta(q[0])
        pose2 = g.SE2_from_xytheta(q[1])
        delta = t[1] - t[0]

        if not delta > 0:
            raise BadInput('Bad timestamp sequence %s' % t, self, 't')

        _, vel = g.SE2.velocity_from_points(pose1, pose2, delta)

        linear, angular = g.linear_angular_from_se2(vel)

        commands = [linear[0], linear[1], angular]
        self.set_output('commands', commands, timestamp=t[0])


# TODO: move this to models/ 
register_model_spec("""
--- model pose2commands
''' Computes the velocity commands from the odometry data. '''

input pose "Odometry as an array ``[x,y,theta]``."

output commands "Estimated commands as an array ``[vx,vy,omega]``."
output vx       "Linear velocity, forward (m/s)"
output vy       "Linear velocity, side (m/s)"
output omega    "Angular velocity (rad/s)"
 
|input name=pose| --> |last_n_samples n=2| --> |pose2vel_| --> commands 

    commands          -->          |output name=commands|
    commands --> |extract index=0| --> |output name=vx|
    commands --> |extract index=1| --> |output name=vy|
    commands --> |extract index=2| --> |output name=omega|
    
""")


register_model_spec("""
--- model commands_from_SE2
''' Computes the velocity commands from the odometry data. '''

input pose "Odometry as an element of SE2."

output commands "Estimated commands as an array ``[vx,vy,omega]``."
output vx       "Linear velocity, forward (m/s)"
output vy       "Linear velocity, side (m/s)"
output omega    "Angular velocity (rad/s)"
 
|input name=pose| --> |last_n_samples n=2| --> |pose2vel_| --> commands 

    commands          -->          |output name=commands|
    commands --> |extract index=0| --> |output name=vx|
    commands --> |extract index=1| --> |output name=vy|
    commands --> |extract index=2| --> |output name=omega|
    
""")

        
