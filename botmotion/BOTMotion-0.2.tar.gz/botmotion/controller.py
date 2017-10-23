#!/usr/bin/env python

import spnav
import math
import threading
import traceback

from profiler import *
from bot_motion import *
#import botmotion

DEBUG = True

VELOCITY_FACTOR = 200
ANGLE_FACTOR = 5

LOW_SPEED_THRESHOLD = 10

MAX_SPEED = 2000
WHEEL_RADIUS = 0.0525  # //in meters
LENGTH_BETWEEN_FRONT_REAR_WHEELS = 0.23  # //in meters
LEGNTH_BETWEEN_FRONT_WHEELS = 0.25  # //in meters
L1 = LEGNTH_BETWEEN_FRONT_WHEELS / 2.0
L2 = LENGTH_BETWEEN_FRONT_REAR_WHEELS / 2.0


class VelocityCalcul(threading.Thread):
    """DOCSTRIN
    g for ClassName"""

    def __init__(self, q_in, q_out_motor):
        super(VelocityCalcul, self).__init__()
        self.q_in = q_in
        self.q_out_motor = q_out_motor
        self.desired_velocity = []
        self.__alive = threading.Event()
        self.__alive.set()


    def e_function(self, val):
        #print val
        ret = math.pow((math.e * (MAX_SPEED / math.e)), math.fabs(val))
        if val > 0:
            return ret
        else:
            return ret * -1

    def high_speed_filter(self, val):
        if (val > MAX_SPEED):
            return MAX_SPEED
        elif (val < -MAX_SPEED):
            return -MAX_SPEED
        else:
            return val


    def close(self):
        #self.q_out_motor.join()
        #self.q_in.join()
        self.__alive.clear()
        #self.join()

    def run(self):
        while self.__alive.isSet():
            if not self.q_in.empty():
                self.desired_velocity = []
                val = self.q_in.get()
                linear_x = val[1]
                linear_y = val[0]*-1
                angular_z = val[2]*-ANGLE_FACTOR
                #print 'X: %f, Y: %f, angle: %f' % (linear_x, linear_y, angular_z)

                # axis0 = ( (-1.0 * (-linear_x + linear_y -  angular_z)) * VELOCITY_FACTOR)
                # axis1 = ( (-1.0 * (-linear_x - linear_y +  (-1.0) * angular_z)) * VELOCITY_FACTOR)
                # axis2 = ( ((-linear_x - linear_y - (-1.0) * angular_z)) * VELOCITY_FACTOR)
                # axis3 = ( ((-linear_x + linear_y + angular_z)) * VELOCITY_FACTOR)
                #
                # axis0 = self.e_function(axis0)
                # axis1 = self.e_function(axis1)
                # axis2 = self.e_function(axis2)
                # axis3 = self.e_function(axis3)
                #
                # # High speed filter
                # axis0 = self.high_speed_filter(axis0)
                # axis1 = self.high_speed_filter(axis1)
                # axis2 = self.high_speed_filter(axis2)
                # axis3 = self.high_speed_filter(axis3)

                axis0 = int( (-1.0 * (-linear_x + linear_y - (L1 + L2) * angular_z) / WHEEL_RADIUS) * VELOCITY_FACTOR)
                axis1 = int( (-1.0 * (-linear_x - linear_y + (L1 + L2) * (-1.0) * angular_z) / WHEEL_RADIUS) * VELOCITY_FACTOR)
                axis2 = int( ((-linear_x - linear_y - (L1 + L2) * (-1.0) * angular_z) / WHEEL_RADIUS) * VELOCITY_FACTOR)
                axis3 = int( ((-linear_x + linear_y + (L1 + L2) * angular_z) / WHEEL_RADIUS) * VELOCITY_FACTOR)

                # Low speed filter
                axis0 = 0 if abs(axis0) < LOW_SPEED_THRESHOLD else axis0
                axis1 = 0 if abs(axis1) < LOW_SPEED_THRESHOLD else axis1
                axis2 = 0 if abs(axis2) < LOW_SPEED_THRESHOLD else axis2
                axis3 = 0 if abs(axis3) < LOW_SPEED_THRESHOLD else axis3

                self.desired_velocity.append(axis0)
                self.desired_velocity.append(axis1)
                self.desired_velocity.append(axis2)
                self.desired_velocity.append(axis3)
                #print "desired velocity = (%f, %f, %f, %f)" % (self.desired_velocity[0], self.desired_velocity[1], self.desired_velocity[2], self.desired_velocity[3])
                self.q_out_motor.put(self.desired_velocity)
                self.q_in.task_done()

        print '[VelCalc] Exit Thread...'


class SpaceNavPosition(threading.Thread):
    def __init__(self, q):
        super(SpaceNavPosition, self).__init__()
        self.q = q
        self.trans = []
        self.__alive = threading.Event()
        self.__alive.set()
        try:
            spnav.spnav_open()
        except spnav.SpnavConnectionException as e:
            raise e


    def close(self):
        self.__alive.clear()
        #print '[SpNav] Shutdown'
        threading.Thread.join(self, None)
        spnav.spnav_close()

    def run(self):
        while self.__alive.isSet():
            event = spnav.spnav_poll_event()

            if event and event.ev_type == spnav.SPNAV_EVENT_MOTION:
                self.trans = []
                self.trans.append(event.translation[2]/350.0)
                self.trans.append(event.translation[0]/350.0)
                self.trans.append(event.rotation[1]/350.0)
                self.q.put(self.trans)
            else:
                self.trans = []
                self.trans.append(0.0)
                self.trans.append(0.0)
                self.trans.append(0.0)
                self.q.put(self.trans)

            spnav.spnav_remove_events(spnav.SPNAV_EVENT_ANY)
            spnav.spnav_remove_events(spnav.SPNAV_EVENT_MOTION)
            spnav.spnav_remove_events(spnav.SPNAV_EVENT_BUTTON)
            time.sleep(0.05)

        print '[SpNav] Exit Thread...'

def debug(motor_list, printer):
    motor = 1

    motor_list.append(BotMotion('192.168.101.221', OPMODE_CSP))
    #motor_list.append(BotMotion('192.168.101.222', OPMODE_CSV))
    #motor_list.append(BotMotion('192.168.101.223', OPMODE_CSV))
    #motor_list.append(BotMotion('192.168.101.224', OPMODE_CSV))

    #profiler = Velocity_Profiler(500, 0, math.pi/400)



    printer.init()

    pdo_in = motor_list[0].get_pdo_in()
    pdo_out = motor_list[0].get_pdo_out()
    profiler = Position_Profiler(pdo_in.position_actual)
    #profiler = Position_Profiler(2000)
    counter = 0
    l_velo = {0, 0, 0, 0}

    # sdo_entry = motor_list[0].upload_sdo_entry(0x2001, 0)
    # print 'Index', sdo_entry.index
    # print 'Subindex', sdo_entry.subindex
    # print 'Value', sdo_entry.value

    while True:
        #for i in range(motor):
            #motor_list[i].set_velocity(profiler.sinus_next_velocity())
            #motor_list[i].set_position(profiler.next_pos())
            #print profiler.next_pos()

            # velo = profiler.next_velocity()
            #motor_list[0].set_velocity(l_velo[0])
            #motor_list[1].set_velocity(500)
            #motor_list[2].set_velocity(500)
            #motor_list[3].set_velocity(500)

        for i in range(motor):
            pdo_in = motor_list[i].get_pdo_in()
            pdo_out = motor_list[i].get_pdo_out()
            printer.print_pdo(pdo_in, pdo_out, i)

def fts(motor_list, printer):

    print ("Move the Space Navigator to control the robot..")

    q_input_dev = Queue.Queue()
    q_motor = Queue.Queue()

    spnavThread = SpaceNavPosition(q_input_dev)
    spnavThread.start()

    velocityCalculator = VelocityCalcul(q_input_dev, q_motor)
    velocityCalculator.start()
    q_input_dev.join()

    motor_list.append(BotMotion('192.168.101.221', OPMODE_CSV))
    motor_list.append(BotMotion('192.168.101.222', OPMODE_CSV))
    motor_list.append(BotMotion('192.168.101.223', OPMODE_CSV))
    motor_list.append(BotMotion('192.168.101.224', OPMODE_CSV))
    printer.init()
    l_velo = {0, 0, 0, 0}

    while True:
        if not q_motor.empty():
            l_velo = q_motor.get()
            q_motor.task_done()

            for i in range(4):
                motor_list[i].set_velocity(l_velo[i])

        for i in range(4):
            pdo_in = motor_list[i].get_pdo_in()
            pdo_out = motor_list[i].get_pdo_out()
            printer.print_pdo(pdo_in, pdo_out, i)


# main
def main():



    spnavThread = None
    velocityCalculator = None
    joystickThread = None
    motor_list = []
    printer = None


    try:

        #profiler = Velocity_Profiler()

        printer = Printing()

        debug(motor_list, printer)
        #fts(motor_list, printer)


    except Exception as e:
        print '#' * 40
        print '\tException:', e
        traceback.print_exc()
        print '#' * 40
        print 'Exit...'
    except KeyboardInterrupt:
        print 'Exit...'
    finally:
        if printer:
            printer.close()
        for motor in motor_list:
            motor.close()

        if velocityCalculator:
            velocityCalculator.close()

        if spnavThread:
            spnavThread.close()

    sys.exit(0)

if __name__ == '__main__':
    main()




