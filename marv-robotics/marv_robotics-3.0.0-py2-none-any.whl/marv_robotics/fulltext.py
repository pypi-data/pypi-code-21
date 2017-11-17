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

from roslib.message import get_message_class

import marv
from marv_nodes.types_capnp import Words
from .bag import messages


@marv.node(Words)
@marv.input('stream', foreach=messages['*:std_msgs/String'])
def fulltext_per_topic(stream):
    yield marv.set_header()  # TODO: workaround
    words = set()
    pytype = get_message_class(stream.msg_type)
    rosmsg = pytype()
    while True:
        msg = yield marv.pull(stream)
        if msg is None:
            break
        rosmsg.deserialize(msg.data)
        words.update(rosmsg.data.split())
    if not words:
        raise marv.Abort()
    yield marv.push({'words': list(words)})


@marv.node(Words)
@marv.input('streams', default=fulltext_per_topic)
def fulltext(streams):
    """Extract all text from bag file and store for fulltext search"""
    tmp = []
    while True:
        stream = yield marv.pull(streams)
        if stream is None:
            break
        tmp.append(stream)
    streams = tmp
    if not streams:
        raise marv.Abort()

    msgs = yield marv.pull_all(*streams)
    words = {x for msg in msgs for x in msg.words}
    yield marv.push({'words': list(words)})
