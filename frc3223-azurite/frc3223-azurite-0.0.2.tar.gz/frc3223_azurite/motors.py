import math
from .conversions import rpm_to_radps


class MotorParams:
    def __init__(self, name, stall_torque, stall_current, free_speed, voltage=12):
        self.name = name
        self.stall_torque = stall_torque # Nm
        self.stall_current = stall_current # A
        self.free_speed = free_speed # rad/s
        self.spec_voltage = voltage # V

    def torque_at_current(self, current_a):
        k = self.ktorque()
        return current_a * k

    def current_at_torque(self, torque_nm):
        k = self.ktorque()
        return torque_nm / k

    def ktorque(self):
        return self.stall_torque / self.stall_current

    def kspeed(self):
        return self.spec_voltage / self.free_speed

    def resistance(self):
        return self.spec_voltage * self.ktorque() / self.stall_torque

    def torque_at_speed(self, invel_radps):
        out_torque = self.stall_torque 
        out_torque *= (self.free_speed - invel_radps) / self.free_speed
        return out_torque 

    def torque_at_speed_and_voltage(self, invel_radps, voltage_v):
        a = voltage_v - invel_radps * self.kspeed() 
        return a * self.ktorque() / self.resistance()

    def speed_at_torque(self, intorque_Nm):
        out_vel_radps = (1 - intorque_Nm / self.stall_torque) * self.free_speed
        return out_vel_radps 

    def speed_at_torque_and_voltage(self, intorque_Nm, voltage_v):
        a = voltage_v - intorque_Nm * self.resistance() / self.ktorque()
        return a / self.kspeed()


class MotorSystem:
    def __init__(self, motor, motor_count, gearing_ratio):
        self.motor = motor
        self.motor_count = motor_count
        self.gearing_ratio = gearing_ratio

    def _t_motor_to_sys(self, motor_torque_nm):
        return motor_torque_nm * self.motor_count * self.gearing_ratio

    def _t_sys_to_motor(self, torque_nm):
        return torque_nm / self.motor_count / self.gearing_ratio

    def _v_motor_to_sys(self, motor_vel_radps):
        return motor_vel_radps / self.gearing_ratio

    def _v_sys_to_motor(self, motor_vel_radps):
        return motor_vel_radps * self.gearing_ratio

    @property
    def name(self):
        return self.motor.name

    @property 
    def stall_torque(self):
        return self._t_motor_to_sys(self.motor.stall_torque)

    @property
    def free_speed(self):
        return self._v_motor_to_sys(self.motor.free_speed)

    def torque_at_motor_current(self, motor_current_a):
        k = self.motor.ktorque()
        motor_torque = motor_current_a * k
        return motor_torque * self.motor_count * self.gearing_ratio

    def motor_current_at_torque(self, torque_nm):
        motor_torque_nm = torque_nm / self.motor_count / self.gearing_ratio
        k = self.motor.ktorque()
        return motor_torque_nm / k

    def torque_at_speed(self, invel_radps):
        motor_speed = self._v_sys_to_motor(invel_radps)
        motor_torque = self.motor.torque_at_speed(motor_speed)
        return self._t_motor_to_sys(motor_torque)

    def torque_at_speed_and_voltage(self, invel_radps, voltage_v):
        motor_speed = self._v_sys_to_motor(invel_radps)
        motor_torque = self.motor.torque_at_speed_and_voltage(motor_speed, voltage_v)
        return self._t_motor_to_sys(motor_torque)

    def speed_at_torque(self, intorque_Nm):
        motor_torque = self._t_sys_to_motor(intorque_Nm)
        motor_speed = self.motor.speed_at_torque(motor_torque)
        return self._v_motor_to_sys(motor_speed)

    def speed_at_torque_and_voltage(self, intorque_Nm, voltage_v):
        motor_torque = self._t_sys_to_motor(intorque_Nm)
        motor_speed = self.motor.speed_at_torque_and_voltage(motor_torque, voltage_v)
        return self._v_motor_to_sys(motor_speed)


cim = MotorParams(
    name="cim", 
    stall_torque=2.41, 
    stall_current=133., 
    free_speed=rpm_to_radps(5300.))

minicim = MotorParams(
    name="minicim", 
    stall_torque=1.4, 
    stall_current=86., 
    free_speed=rpm_to_radps(6200.))

bag = MotorParams(
    name="bag", 
    stall_torque=0.4, 
    stall_current=41., 
    free_speed=rpm_to_radps(14000.))

_775pro = MotorParams(
    name="775pro", 
    stall_torque=0.71, 
    stall_current=134., 
    free_speed=rpm_to_radps(18730.))

rs775 = MotorParams(
    name="rs775", 
    stall_torque=0.247, 
    stall_current=22., 
    free_speed=rpm_to_radps(5700.))

am9015 = MotorParams(
    name="am9015", 
    stall_torque=0.428, 
    stall_current=63.8, 
    free_speed=rpm_to_radps(16000.))
