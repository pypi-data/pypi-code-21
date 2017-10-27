"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        verify.py

    FIRST RELEASE
        2017-07-31  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import re


def verify_sensor_id(sensor_id):
    """check if the sensor_id matches `[a-Z0-9_]+`"""
    pattern = r"^[a-zA-Z0-9_]+$"
    if re.match(pattern, sensor_id) is None:
        raise ValueError(
            ('Sensor ID "%s" uses illegal character.\nOnly ASCII characters, '
             'numbers and underscore are allowed.') % sensor_id)

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
