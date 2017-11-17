# -*- coding: utf-8 -*-
#
# This file is part of MARV Robotics
#
# Copyright 2016-2017 Ternaris
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

from datetime import datetime

import matplotlib; matplotlib.use('Agg')
import numpy as np
import utm
from matplotlib import cm
from matplotlib import dates as md
from matplotlib import pyplot as plt
from roslib.message import get_message_class

import marv
from marv_nodes.types_capnp import File
from .bag import messages


def yaw_angle(frame):
    rot = np.zeros((3, 3))

    # consists of time, x, y, z, w
    q1 = frame.x
    q2 = frame.y
    q3 = frame.z
    q4 = frame.w

    rot[0, 0] = 1 - 2 * q2 * q2 - 2 * q3 * q3
    rot[0, 1] = 2 * (q1 * q2 - q3 * q4)
    rot[0, 2] = 2 * (q1 * q3 + q2 * q4)
    rot[1, 0] = 2 * (q1 * q2 + q3 * q4)
    rot[1, 1] = 1 - 2 * q1 * q1 - 2 * q3 * q3
    rot[1, 2] = 2 * (q2 * q3 - q1 * q4)
    rot[2, 0] = 2 * (q1 * q3 - q2 * q4)
    rot[2, 1] = 2 * (q1 * q4 + q2 * q3)
    rot[2, 2] = 1 - 2 * q1 * q1 - 2 * q2 * q2

    vec = np.dot(rot, [1, 0, 0])
    return np.arctan2(vec[1], vec[0])


@marv.node()
@marv.input('stream', foreach=messages['*:sensor_msgs/NavSatFix'])
def positions(stream):
    yield marv.set_header(title=stream.topic)
    pytype = get_message_class(stream.msg_type)
    rosmsg = pytype()
    erroneous = 0
    e_offset = None
    n_offset = None
    u_offset = None
    positions = []
    while True:
        msg = yield marv.pull(stream)
        if msg is None:
            break
        rosmsg.deserialize(msg.data)
        if not hasattr(rosmsg, 'status') or \
           np.isnan(rosmsg.longitude) or \
           np.isnan(rosmsg.latitude) or \
           np.isnan(rosmsg.altitude):
            erroneous += 1
            continue

        e, n, _, _ = utm.from_latlon(rosmsg.longitude, rosmsg.latitude)
        if e_offset is None:
            e_offset = e
            n_offset = n
            u_offset = rosmsg.altitude
        e = e - e_offset
        n = n - n_offset
        u = rosmsg.altitude - u_offset

        # TODO: why do we accumulate?
        positions.append([rosmsg.header.stamp.to_sec(),
                          rosmsg.latitude,
                          rosmsg.longitude,
                          rosmsg.altitude,
                          e, n, u,
                          rosmsg.status.status,
                          np.sqrt(rosmsg.position_covariance[0])])
    if erroneous:
        log = yield marv.get_logger()
        log.warn('skipped %d erroneous messages', erroneous)
    yield marv.push({'values': positions})


@marv.node()
@marv.input('stream', foreach=messages['*:sensor_msgs/Imu'])
def imus(stream):
    yield marv.set_header(title=stream.topic)
    pytype = get_message_class(stream.msg_type)
    rosmsg = pytype()
    erroneous = 0
    imus = []
    while True:
        msg = yield marv.pull(stream)
        if msg is None:
            break
        rosmsg.deserialize(msg.data)
        if np.isnan(rosmsg.orientation.x):
            erroneous += 1
            continue

        # TODO: why do we accumulate?
        imus.append([rosmsg.header.stamp.to_sec(), yaw_angle(rosmsg.orientation)])
    if erroneous:
        log = yield marv.get_logger()
        log.warn('skipped %d erroneous messages', erroneous)
    yield marv.push({'values': imus})


@marv.node()
@marv.input('stream', foreach=messages['*:nmea_navsat_driver/NavSatOrientation'])
def navsatorients(stream):
    log = yield marv.get_logger()
    yield marv.set_header(title=stream.topic)
    pytype = get_message_class(stream.msg_type)
    if pytype is None:
        log.error('Message definition for %r not available', stream.msg_type)
        raise marv.Abort()
    rosmsg = pytype()
    erroneous = 0
    navsatorients = []
    while True:
        msg = yield marv.pull(stream)
        if msg is None:
            break

        rosmsg.deserialize(msg.data)
        if np.isnan(rosmsg.yaw):
            erroneous += 1
            continue

        # TODO: why do we accumulate?
        navsatorients.append([rosmsg.header.stamp.to_sec(), rosmsg.yaw])
    if erroneous:
        log.warn('skipped %d erroneous messages', erroneous)
    yield marv.push({'values': navsatorients})


@marv.node(group=True)
@marv.input('imus', default=imus)
@marv.input('navsatorients', default=navsatorients)
def orientations(imus, navsatorients):
    while True:
        tmp = yield marv.pull(imus)
        if tmp is None:
            break
        yield marv.push(tmp)
    while True:
        tmp = yield marv.pull(navsatorients)
        if tmp is None:
            break
        yield marv.push(tmp)


@marv.node(File)
#@marv.input('gps', foreach=positions)
#@marv.input('orientation', foreach=orientations)
@marv.input('gps', default=positions)
@marv.input('orientation', default=orientations)
def gnss_plots(gps, orientation):
    # TODO: framework does not yet support multiple foreach
    # pick only first combination for now

    log = yield marv.get_logger()
    gps, orientation = yield marv.pull_all(gps, orientation)
    if gps is None:
        log.error('No gps messages')
        raise marv.Abort()
    gtitle = gps.title

    gps = yield marv.pull(gps)  # There is only one message
    gps = gps['values']
    if orientation is not None:
        otitle = orientation.title
        orientation = yield marv.pull(orientation)
    if orientation is None:
        log.warn('No orientations found')
        otitle = 'none'
        orientation = []
    else:
        orientation = orientation['values']

    name = '__'.join(x.replace('/', ':')[1:] for x in [gtitle, otitle]) + '.jpg'
    title = '{} with {}'.format(gtitle, otitle)
    yield marv.set_header(title=title)
    plotfile = yield marv.make_file(name)

    fig = plt.figure()
    fig.subplots_adjust(wspace=0.3)

    ax1 = fig.add_subplot(1, 3, 1)  # e-n plot
    ax2 = fig.add_subplot(2, 3, 2)  # orientation plot
    ax3 = fig.add_subplot(2, 3, 3)  # e-time plot
    ax4 = fig.add_subplot(2, 3, 5)  # up plot
    ax5 = fig.add_subplot(2, 3, 6)  # n-time plot

    # masking for finite values
    gps = np.array(gps)
    gps = gps[np.isfinite(gps[:, 1])]

    # precompute plot vars
    c = cm.prism(gps[:, 7]/2)

    ax1.scatter(gps[:, 4], gps[:, 5], c=c, edgecolor='none', s=3,
                label="green: RTK\nyellow: DGPS\nred: Single")

    xfmt = md.DateFormatter('%H:%M:%S')
    ax3.xaxis.set_major_formatter(xfmt)
    ax4.xaxis.set_major_formatter(xfmt)
    ax5.xaxis.set_major_formatter(xfmt)

    if orientation:
        ax2.xaxis.set_major_formatter(xfmt)
        orientation = np.array(orientation)
        ax2.plot([datetime.fromtimestamp(x) for x in orientation[:, 0]],
                 orientation[:, 1])

    ax3.plot([datetime.fromtimestamp(x) for x in gps[:, 0]], gps[:, 4])
    ax4.plot([datetime.fromtimestamp(x) for x in gps[:, 0]], gps[:, 6])
    ax5.plot([datetime.fromtimestamp(x) for x in gps[:, 0]], gps[:, 5])

    fig.autofmt_xdate()

    ax1.legend(loc='upper right', title='')

    ax1.set_ylabel('GNSS northing [m]')
    ax1.set_xlabel('GNSS easting [m]')
    ax2.set_ylabel('Heading over time [rad]')
    ax3.set_ylabel('GNSS easting over time [m]')
    ax4.set_ylabel('GNSS height over time [m]')
    ax5.set_ylabel('GNSS northing over time [m]')

    fig.set_size_inches(16, 9)
    try:
        fig.savefig(plotfile.path)
    except:
        plt.close()
    yield plotfile
