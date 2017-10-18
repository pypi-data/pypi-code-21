# -*- coding: utf-8 -*-


from datetime import datetime


def to_ms_timestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt - epoch
    return ((td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**3)


def to_ms_timestamp_int(dt, epoch=datetime(1970, 1, 1)):
    ts = to_ms_timestamp(dt, epoch)

    return int(ts)
