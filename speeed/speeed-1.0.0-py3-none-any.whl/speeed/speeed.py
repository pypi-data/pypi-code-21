#!/usr/bin/env python3

"""
speeed - ping like tool that measures packet speed instead of response time

Usage:
  speeed [-4 | -6] <dest>
  speeed (-h | --help)
  speeed --version

Options:
  -h, --help        Show this screen.
  --version         Show version.
  -4                Use IPv4 (default).
  -6                Use IPv6.
"""

__author__ = "Ricardo Band"
__copyright__ = "Copyright 2017, Ricardo Band"
__credits__ = ["Ricardo Band", ]
__licence__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ricardo Band"
__email__ = "email@ricardo.band"
__status__ = "Production"


import sys
import json
import socket
from subprocess import Popen, PIPE
from math import sin, cos, sqrt, atan2, radians

import requests
from docopt import docopt


def cli():
    """
    """
    speeed = Speeed()
    speeed.start()


class Speeed:
    def __init__(self):
        self.args = docopt(__doc__, version=__version__)
        self.dest = self.args["<dest>"]
        if self.args["-6"]:
            self.ipver = "-6"
            try:
                # [(family, type, proto, canonname, sockaddr)]
                self.dest_ip = socket.getaddrinfo(self.dest, None, socket.AF_INET6)[0][4][0]
            except socket.gaierror:
                sys.exit("%s is or has no IPv6 address" % self.dest)
            r = requests.get("https://v6.ident.me/.json")
        else:
            self.ipver = "-4"
            try:
                # [(family, type, proto, canonname, sockaddr)]
                self.dest_ip = socket.getaddrinfo(self.dest, None, socket.AF_INET)[0][4][0]
            except socket.gaierror:
                sys.exit("%s is or has no IPv4 address" % self.dest)
            r = requests.get("https://v4.ident.me/.json")
        self.src_ip = json.loads(r.text)["address"]
        self.src_location = self.ip2location(self.src_ip)
        self.dest_location = self.ip2location(self.dest_ip)

        self.distance = self.get_distance()

        if self.dest != self.dest_ip:
            print("distance to %s (%s): %d km" % (self.dest, self.dest_ip, self.distance))
        else:
            print("distance to %s: %d km" % (self.dest_ip, self.distance))

    def get_distance(self):
        """
        Calculate distance between source IP and destination IP.

        :return: distance in km
        """
        # approximate radius of earth in km
        R = 6371.0

        lat1 = radians(self.src_location[0])
        lon1 = radians(self.src_location[1])
        lat2 = radians(self.dest_location[0])
        lon2 = radians(self.dest_location[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def start(self):
        """

        :return:
        """
        proc = Popen(["ping", self.ipver, self.dest_ip], stdout=PIPE)
        try:
            while True:
                line = proc.stdout.readline().decode().strip()
                self.calc_speed(pingline=line)
        except KeyboardInterrupt:
            proc.terminate()
        print()

    def ip2location(self, ip):
        """
        Returns latitude and longitude of a IP.

        :param ip: IPv4 or IPv6 address
        :type ip: str
        :return:
        """
        url = "http://freegeoip.net/json/%s" % ip

        r = requests.get(url)
        data = json.loads(r.text)

        return data['latitude'], data['longitude']

    def calc_speed(self, pingline):
        """

        :param pingline:
        :return:
        """
        if "icmp_seq=" in pingline:
            lightspeed = 299792.458
            if self.distance == 0:
                speed = lightspeed
            else:
                t = float(pingline.split("time=")[1].rstrip(" ms")) / 1000.0
                speed = self.distance / t
            print("speed: ~%06.3f km/s (%d%% speed of light)" % (speed, speed * 100.0 / lightspeed), end="\r")

