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

import numpy as np
from roslib.message import get_message_class

import marv
from marv_nodes.types_capnp import File, GeoJson
from .bag import messages


@marv.node()
@marv.input('stream', foreach=messages['*:sensor_msgs/NavSatFix'])
def navsatfix(stream):
    yield marv.set_header(title=stream.topic)
    pytype = get_message_class(stream.msg_type)
    rosmsg = pytype()
    erroneous = 0
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
        # TODO: namedtuple?
        out = {'status': rosmsg.status.status,
               'lon': rosmsg.longitude, 'lat': rosmsg.latitude}
        yield marv.push(out)
    if erroneous:
        log = yield marv.get_logger()
        log.warn('skipped %d erroneous messages', erroneous)


@marv.node(GeoJson)
@marv.input('navsatfixes', default=navsatfix)
def trajectory(navsatfixes):
    navsatfix = yield marv.pull(navsatfixes)  # Only one topic for now
    if not navsatfix:
        raise marv.Abort()
    yield marv.set_header(title=navsatfix.title)
    features = []
    prev_quality = None
    while True:
        msg = yield marv.pull(navsatfix)
        if msg is None:
            break
        # Whether to output an augmented fix is determined by both the fix
        # type and the last time differential corrections were received.  A
        # fix is valid when status >= STATUS_FIX.
        # STATUS_NO_FIX =  -1 -> unable to fix position       -> color id 0 = red
        # STATUS_FIX =      0 -> unaugmented fix              -> color id 1 = orange
        # STATUS_SBAS_FIX = 1 -> satellite-based augmentation -> color id 2 = blue
        # STATUS_GBAS_FIX = 2 -> ground-based augmentation    -> color id 3 = green
        #                     -> unknown status id            -> color id 4 = black
        if -1 <= msg['status'] <= 2:
            quality = msg['status'] + 1
        else:
            quality = 4
        if quality != prev_quality:
            color = ((255,   0,   0, 255),  # rgba
                     (255, 165,   0, 255),
                     (  0,   0, 255, 255),
                     (  0, 255,   0, 255))[quality]
            coords = []
            feat = {'properties': {'color': color},
                    'geometry': {'line_string': {'coordinates': coords}}}
            features.append(feat)
            prev_quality = quality
        coords.append((msg['lon'], msg['lat']))
    if features:
        out = {'feature_collection': {'features': features}}
        yield marv.push(out)
