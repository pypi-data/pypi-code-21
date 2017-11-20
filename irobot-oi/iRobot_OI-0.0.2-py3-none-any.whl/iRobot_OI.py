#!/usr/bin/env python

"""iRobot OI Python Interface
"""

import serial
import time

oi = serial.Serial('/dev/ttyAMA0', baudrate=57600)

class utils:

    @staticmethod
    def sendOpcode(opcode):
        oi.write(chr(opcode))

    @staticmethod
    def sendBytes(*args):
        oi.write(bytearray(args))

def start():
    """
    This command starts the OI.

    Available in modes: Passive, Safe, or Full
    Changes mode to: Passive. Create beeps once to acknowledge it is starting
    from “off” mode.
    """

    utils.sendOpcode(128)

def baud(baudRate):
    """
    This command sets the baud rate in bits per second (bps) at which OI
    commands and data are sent.

    Available in modes: Passive, Safe, or Full
    Changes mode to: No Change

    Data byte 1: Baud Code (0 - 11)
    """

    utils.sendOpcode(129)
    baudCodes = {
        300:    chr(0),
        600:    chr(1),
        1200:   chr(2),
        2400:   chr(3),
        4800:   chr(4),
        9600:   chr(5),
        14400:  chr(6),
        19200:  chr(7),
        28800:  chr(8),
        38400:  chr(9),
        57600:  chr(10),
        115200: chr(11),
    }
    baudCode = baudCodes.get(baudRate, -1)
    if baudCode == -1:
        raise ValueError("Invalid baud rate!")
    oi.write(baudCode)
    time.sleep(0.1)
    oi.baudrate = baudRate

class mode:

    def safe():
        """
        This command puts the OI into Safe mode, enabling user control of
        Create. It turns off all LEDs.

        Available in modes: Passive, Safe, or Full
        Changes mode to: Safe
        """

        utils.sendOpcode(131)

    def full():
        """
        This command gives you complete control over Create by putting the OI
        into Full mode, and turning off the cliff, wheel-drop and internal
        charger safety features.

        Available in modes: Passive, Safe, or Full
        Changes mode to: Full
        """

        utils.sendOpcode(132)

class actuator:

    @staticmethod
    def drive(velocity, radius):
        """
        This command controls Create’s drive wheels.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Velocity (-500 – 500 mm/s)
        Argument 2: Radius (-2000 – 2000 mm)

        Special cases:
        Velocity = 128, Radius = 0   -> Straight
        Velocity = 127, Radius = 255 -> Straight
        Velocity = 255, Radius = 255 -> In-place CW
        Velocity = 0  , Radius = 1   -> In-place CCW
        """

        utils.sendOpcode(137)
        velHi = velocity >> 8
        velLo = velocity & 0xff
        radHi = radius >> 8
        radLo = radius & 0xff
        utils.sendBytes(velHi, velLo, radHi, radLo)

    @staticmethod
    def driveDirect(rightVelocity, leftVelocity):
        """
        This command lets you control the forward and backward motion of
        Create’s drive wheels independently.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Right wheel velocity (-500 – 500 mm/s)
        Argument 2: Left wheel velocity (-500 – 500 mm/s)
        """

        utils.sendOpcode(145)
        rvHi = rightVelocity >> 8
        rvLo = rightVelocity & 0xff
        lvHi = leftVelocity >> 8
        lvLo = leftVelocity & 0xff
        utils.sendBytes(rvHi, rvLo, lvHi, lvLo)

    @staticmethod
    def leds(advance, play, powerColor, powerIntensity):
        """
        This command controls the LEDs on Create.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Advance LED (false = off, true = on)
        Argument 2: Play LED (false = off, true = on)
        Argument 3: Power LED Color (0 – 255) 0 = green, 255 = red.
        Argument 4: Power LED Intensity (0 – 255) 0 = off, 255 = full intensity
        """

        utils.sendOpcode(139)
        advPlay = 0
        if advance:
            advPlay |= 0b00001000
        if play:
            advPlay |= 0b00000010
        utils.sendBytes(advPlay, powerColor, powerIntensity)

    @staticmethod
    def digitalOutputs(out0, out1, out2):
        """
        This command controls the state of the 3 digital output pins on the 25
        pin Cargo Bay Connector.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Digital Out 0 (false = low/0V, true = high/5V)
        Argument 2: Digital Out 1 (false = low/0V, true = high/5V)
        Argument 3: Digital Out 2 (false = low/0V, true = high/5V)
        """

        utils.sendOpcode(147)
        out = 0
        if out2:
            out |= 0b00000100
        if out1:
            out |= 0b00000010
        if out0:
            out |= 0b00000001
        utils.sendBytes(out)

    @staticmethod
    def pwmLowSideDrivers(driver0, driver1, driver2):
        """
        This command lets you control the three low side drivers with variable
        power.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Duty cycle for low side driver 0 (0 - 128)
        Argument 2: Duty cycle for low side driver 1 (0 - 128)
        Argument 3: Duty cycle for low side driver 2 (0 - 128)
        """

        utils.sendOpcode(144)
        utils.sendBytes(driver2, driver1, driver0)

    @staticmethod
    def lowSideDrivers(driver0, driver1, driver2):
        """
        This command lets you control the three low side drivers.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Low Side Driver 0 (false = off, true = on) 0.5A
        Argument 2: Low Side Driver 1 (false = off, true = on) 0.5A
        Argument 3: Low Side Driver 2 (false = off, true = on) 1.5A
        """

        utils.sendOpcode(138)
        drivers = 0
        if driver2:
            out |= 0b00000100
        if driver1:
            out |= 0b00000010
        if driver0:
            out |= 0b00000001
        utils.sendBytes(drivers)

    @staticmethod
    def sendIR(byteValue):
        """
        This command sends the requested byte out of low side driver 1 (pin 23
        on the Cargo Bay Connector), using the format expected by iRobot
        Create’s IR receiver.

        Available in modes: Safe or Full
        Changes mode to: No Change

        Argument 1: Byte value to send (0 - 255)
        """

        utils.sendOpcode(151)
        utils.sendBytes(byteValue)

class input:

    @staticmethod
    def sensors(packetID):
        """
        This command requests the OI to send a packet of sensor data bytes.

        Available in modes: Passive, Safe, or Full
        Changes mode to: No Change

        Argument 1: Packet ID (0 - 42)
        """

        utils.sendOpcode(142)
        utils.sendBytes(packetID)

    @staticmethod
    def queryList(*packetIDs)
        """
        This command lets you ask for a list of sensor packets.

        Available in modes: Passive, Safe, or Full
        Changes mode to: No Change

        Argument 1: IDs of packets requested (0 - 42)
        """

        utils.sendOpcode(149)
        utils.sendBytes(len(packetIDs))
        utils.sendBytes(packetIDs)

class wait:

    @staticmethod
    def waitTime(time):
        """
        This command causes Create to wait for the specified time.

        Available in modes: Passive, Safe, or Full
        Changes mode to: No Change

        Argument 1: Time (0 - 255) in tenths of a second, resolution of 15 ms
        """

        utils.sendOpcode(155)
        utils.sendBytes(time)

    @staticmethod
    def waitDistance(distance):
        """
        This command causes iRobot Create to wait until it has traveled the specified distance in mm.

        Available in modes: Passive, Safe, or Full
        Changes mode to: No Change

        Argument 1: Distance in mm (-32767 - 32768)
        """

        utils.sendOpcode(156)
        distHi = distance >> 8
        distLo = distance & 0xff
        utils.sendBytes(distHi, distLo)

    @staticmethod
    def waitAngle(angle):
        """
        This command causes Create to wait until it has rotated through speci ed angle in degrees.

        Available in modes: Passive, Safe, or Full
        Changes mode to: No Change

        Argument 1: Angle in degrees (-32767 - 32768)
        """

        utils.sendOpcode(157)
        angHi = angle >> 8
        angLo = angle & 0xff
        utils.sendBytes(angHi, angLo)
