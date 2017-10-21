
import logging
import socket
import time

from collections import namedtuple
from enum import Enum
from queue import Queue
from threading import Thread, Event

GROUP_ALL = 0
NUM_GROUPS = 5 # Including group 0 (all)

# White LEDs command set
WHITE_CMD = 0x01
WHITE_CMD_SET_BRIGHTNESS = 0x0d
WHITE_CMD_SET_temperature = 0x0e
WHITE_CMD_SET = 0x1a

WHITE_CMD_ALL_ON  = 0x01
WHITE_CMD_ALL_OFF = 0x02
WHITE_CMD_CH1_ON  = 0x03
WHITE_CMD_CH1_OFF = 0x04
WHITE_CMD_CH2_ON  = 0x05
WHITE_CMD_CH2_OFF = 0x06
WHITE_CMD_CH3_ON  = 0x07
WHITE_CMD_CH3_OFF = 0x08
WHITE_CMD_CH4_ON  = 0x09
WHITE_CMD_CH4_OFF = 0x0a

white_cmd = [WHITE_CMD_ALL_ON, WHITE_CMD_CH1_ON, WHITE_CMD_CH2_ON, WHITE_CMD_CH3_ON, WHITE_CMD_CH4_ON]

# RGB LEDs command set
RGB_CMD = 0x02
RGB_CMD_SET = 0x11

log = logging.getLogger(__name__)

Color = namedtuple('Color', ['r', 'g', 'b'])
GroupMode = Enum('GroupMode', 'WHITE RGB')

class GroupState:
    __slots__ = ('on', 'mode', 'brightness', 'temperature', 'color')

    def __init__(self, on=False, mode=GroupMode.WHITE, brightness=0, temperature=0, color=Color(0,0,0)):
        self.update(on, mode, brightness, temperature, color)

    def update(self, on=None, mode=None, brightness=None, temperature=None, color=None):
        if on is not None:
            self.on = on

        if mode is not None:
            self.mode = mode

        if brightness is not None:
            self.brightness = brightness

        if temperature is not None:
            self.temperature = temperature

        if color is not None:
            self.color = color


class AbstractBridge:
    def __init__(self, host, port=50000, interval=0.250):
        self.host = host
        self.port = port
        self.interval = interval

        self.last_active = None
        self.group_states = [GroupState() for i in range(5)]

    def reset_state(self):
        pass

    def update_state(self, group, on=None, mode=None, brightness=None, temperature=None, color=None):
        if group == GROUP_ALL:
            for group in range(0, NUM_GROUPS):
                self.group_states[group].update(on, mode, brightness, temperature, color)
        else:
            self.group_states[group].update(on, mode, brightness, temperature, color)

    def _send_on_cmd(self, group, temperature):
        log.debug('sending group: %d, command: on, temperature: %d' % (group, temperature))
        self.send_packet(bytearray((WHITE_CMD, white_cmd[group], temperature, 0x00, 0x55)))

    def _send_off_cmd(self, group):
        log.debug('sending group: %d, command: off' % group)
        self.send_packet(bytearray((WHITE_CMD, white_cmd[group] +  1, 0x00, 0x00, 0x55)))

    def _send_white_cmd(self, temperature, brightness):
        log.debug('sending cmd: white, temperature: %d, brightness: %d' % (temperature, brightness))
        self.send_packet(bytearray((WHITE_CMD, WHITE_CMD_SET, temperature, brightness, 0x55)))

    def _send_rgb_cmd(self, color, brightness):
        log.debug('sending cmd: rgb, color: %r, brightness: %d' % (color, brightness))
        self.send_packet(bytearray((RGB_CMD, RGB_CMD_SET, color.r, color.g, color.b, brightness, 0xff, 0x55)))

    def switch_on(self, group_idx):
        group = self.group_states[group_idx]

        if group.mode == GroupMode.RGB:
            # to make sure we turn on in the rigth color we have to "select"
            # the group first by sending on/off packet and send the rgb cmd
            # before sending and on cmd
            if self.last_active != group_idx:
                if group.on:
                    self._send_on_cmd(group_idx, group.temperature)
                else:
                    self._send_off_cmd(group_idx)
            self._send_rgb_cmd(group.color, group.brightness)

        self._send_on_cmd(group_idx, group.temperature)
        self.update_state(group_idx, on=True)
        self.last_active = group_idx


    def switch_off(self, group_idx):
        self._send_off_cmd(group_idx)
        self.update_state(group_idx, on=False)
        self.last_active = group_idx


    def set_white(self, group_idx, temperature=None, brightness=None):
        group = self.group_states[group_idx]

        if self.last_active != group_idx:
            self.last_active = group_idx
            self._send_on_cmd(group_idx, group.temperature)
            self.update_state(group_idx, on=True)

        if temperature is None:
            termperture = group.temperature

        if brightness is None:
            brightness = group.brightness

        self._send_white_cmd(temperature, brightness)
        self.update_state(group_idx, mode=GroupMode.WHITE, temperature=temperature, brightness=brightness)


    def set_rgb(self, group_idx, color=None, brightness=None):
        group = self.group_states[group_idx]

        if self.last_active != group_idx:
            self.last_active = group_idx
            if group.on:
                self._send_on_cmd(group_idx, group.temperature)
            else:
                self._send_off_cmd(group_idx)

        if color is None:
            color = group.color

        if brightness is None:
            brightness = group.brigthness

        self._send_rgb_cmd(color, brightness)
        self.update_state(group_idx, mode=GroupMode.RGB, brightness=brightness, color=color)

        if not group.on:
            self._send_on_cmd(group_idx, group.temperature)
            self.update_state(group_idx, on=True)


    def send_packet(self, packet):
        raise NotImplementedError


class Bridge(AbstractBridge):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_packet(self, packet):
        self._socket.sendto(packet, (self.host, self.port))
        time.sleep(self.interval)


class BridgeThread(AbstractBridge):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._packet_queue = Queue()
        self._stopped = Event()
        self._pump = None

    def start(self):
        self._stopped.clear()
        self._pump = Thread(target=self._packet_pusher)
        self._pump.start()

    def stop(self):
        self._packet_queue.put(None)
        self._stopped.wait()

    def _packet_pusher(self):
        while True:
            packet = self._packet_queue.get()

            if packet is None:
                break

            self._socket.sendto(packet, (self.host, self.port))
            time.sleep(self.interval)

        self._stopped.set()

    def send_packet(self, packet):
        self._packet_queue.put(packet)

