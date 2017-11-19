from pypot.creatures import AbstractPoppyCreature

from subprocess import call

class RoboticiaMove(AbstractPoppyCreature):
    @classmethod
    def setup(cls, robot):
        for m in robot.motors:
            m.goto_behavior = 'dummy'
            m.moving_speed = 0
            m.pid = (6.0,10.0,0.0)
           
        
        if robot.simulated:
            cls.vrep_hack(robot)


    @classmethod
    def vrep_hack(cls, robot):
        # fix vrep orientation bug
        wrong_motor = []
        
        for m in wrong_motor:
            m.direct = not m.direct
            #m.offset = -m.offset
            
        # use minjerk to simulate speed in vrep
        for m in robot.motors:
            m.goto_behavior = 'minjerk'

        
