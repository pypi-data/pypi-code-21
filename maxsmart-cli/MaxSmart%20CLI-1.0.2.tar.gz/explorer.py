from socket import *
import select
import json
import time
import requests
from requests import Request
from datetime import datetime
import time
import random

from maxsmart_http import MaxsmartHttp

def toDayString(day):
    if day == 0:
        return 'Sun'
    elif day == 1:
        return 'Mon'
    elif day == 2:
        return 'Tue'
    elif day == 3:
        return 'Wed'
    elif day == 4:
        return 'Thu'
    elif day == 5:
        return 'Fri'
    elif day == 6:
        return 'Sat'

class Device:
    def __init__(self, data, ip):
        self.name = data['name']
        self.sn = data['sn']
        self.sak = data['sak']
        self.ip = ip

    def time(self):
        response = MaxsmartHttp.send(self, 502)

        return response.json()['data']['time']

    def set_timer(self, datetime):
        options = {'port': 0, 'start': datetime, 'delay': 60}
        MaxsmartHttp.send(self, 204, options)

    def timer(self):
        options = {'port': 0}
        response = MaxsmartHttp.send(self, 515, options)

        return response.json()['data']

    def add_rule(self, time, state):
        # en = enabled
        # mode == 0 create, mode == 1 update, mode == 2 delete
        # time: in minutes from 00:00
        time = time.split(':')
        minutes = int(time[0]) * 60 + int(time[1])
        random_id = int(random.getrandbits(24))
        state = 1 if state == 'on' else 0

        options = {'mode': 0, 'id': random_id, 'en': 1, 'port': [state], 'time': minutes, 'week': [1,1,1,1,1,1,1]}

        MaxsmartHttp.send(self, 206, options)

    def delete_rule(self, rule_id):
        options = {'mode': 2, 'id': int(rule_id)}
        MaxsmartHttp.send(self, 206, options)

    def rules(self):
        options = {'page': 0}
        response = MaxsmartHttp.send(self, 516, options)

        rules = response.json()['data']['rule']

        for rule in rules:
            action = 'turn on' if rule['port'][0] == 1 else 'turn off'
            hours = str(rule['time'] / 60).zfill(2)
            minutes = str(rule['time'] % 60).zfill(2)
            time = '%s:%s' % (hours, minutes)
            every_day = all(enabled == 1 for enabled in rule['week'])

            if every_day:
                days = 'every day'
            else:
                days = [(toDayString(index) if day_enabled else '') for index, day_enabled in enumerate(rule['week'])]
                days = ' '.join(days).strip()

            print('%s %s %s %s' % (rule['id'], time, action, days))
        

class Explorer:
    def discover(self, broadcast_address):
        cs = socket(AF_INET, SOCK_DGRAM)
        cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        
        utc_offset = -time.timezone / 3600
        now = datetime.now().strftime('%s,%s' % ('%Y-%m-%d,%H:%M:%S', utc_offset))
        cs.sendto('00dv=all,%s;' % now, (broadcast_address, 8888))
        cs.setblocking(0)

        timeToWaitInSeconds = 2
        start_time = time.time()
        devices = []

        while time.time() - start_time <= timeToWaitInSeconds:
            ready = select.select([cs], [], [], timeToWaitInSeconds)

            if ready[0]:
                # A buffer of 1024 is also used in the Android app of MaxSmart.
                # We assume this suffices.
                data, address = cs.recvfrom(1024)
                parsed = json.loads(data)
                devices.append(Device(parsed['data'], address[0]))

        return devices

    def status(self, device):
        response = MaxsmartHttp.send(device, 511)

        return response.json()['data']

    def switch(self, device, status):
        new_state = 1 if status == 'on' else 0
        options = {'port': '0', 'state': new_state}

        MaxsmartHttp.send(device, 200, options)

    def set_name(self, device, name):
        options = {'port': '0', 'name': name}

        MaxsmartHttp.send(device, 201, options)
