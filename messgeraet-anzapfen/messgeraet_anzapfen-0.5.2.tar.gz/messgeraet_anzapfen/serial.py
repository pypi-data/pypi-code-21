"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        serial.py

    DESCRIPTION

    FIRST RELEASE
        2017-07-18    Sebastian Stigler    sebastian.stigler@hs-aalen.de

"""
import hashlib


def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
    except (OSError, IOError):
        cpuserial = "ERROR000000000"

    macaddress = "00:00:00:00:00:00"
    try:
        with open('/sys/class/net/eth0/address', 'r') as eth0address:
            data = eth0address.read().strip()
        if data:
            macaddress = data
    except (OSError, IOError):
        macaddress = "ba:da:ff:ed:ea:dc"

    return cpuserial, macaddress


def hashserial():
    cpu, mac = getserial()
    md5sum = hashlib.md5()
    md5sum.update(cpu.encode('ascii'))
    md5sum.update(mac.encode('ascii'))
    return md5sum.hexdigest()


if __name__ == '__main__':
    print(getserial())
    print(hashserial())

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
