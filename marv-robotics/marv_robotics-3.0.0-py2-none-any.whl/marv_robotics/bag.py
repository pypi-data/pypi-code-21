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

import os
import re
import sys
from collections import defaultdict, namedtuple
from itertools import groupby
from logging import getLogger

import capnp
import genpy
import rosbag

import marv
import marv_nodes
from marv.scanner import DatasetInfo
from .bag_capnp import Bagmeta, Header, Message


_Baginfo = namedtuple('Baginfo', ('filename', 'name', 'timestamp', 'idx'))
class Baginfo(_Baginfo):
    def __new__(cls, filename, name, timestamp=None, idx=None):
        idx = None if idx is None else int(idx)
        return super(Baginfo, cls).__new__(cls, filename, name, timestamp, idx)


def scan(dirpath, dirnames, filenames):
    """Default scanner for ROS bag files

    The file naming convention employed by ``rosbag record`` is
    understood to create sets of split bags. Bags that do not fit that
    naming convention will be treated as individual datasets.

    For more information on scanners see :any:`marv.scanner`.

    Args:
        dirpath (str): The path to the directory currently being
            scanned.
        dirnames (str): Sorted list of subdirectories of the directory
            currently being scanned.  Change this in-place to control
            further traversal.
        filenames (str): Sorted list of files within the directory
            currently being scanned.

    Returns:
        A list of :class:`marv.scanner.DatasetInfo` instances mapping
        set of files to dataset names.  Absolute filenames must
        start with :paramref:`.dirpath`, relative filenames are
        automatically prefixed with it.

    See :ref:`cfg_c_scanner` config key.
    """
    log = getLogger('{}.{}'.format(__name__, 'scan'))
    regex = re.compile(r'^(.+?)(?:_(\d{4}(?:-\d{2}){5})_(\d+))?.bag$')
    groups = groupby([Baginfo(x, *re.match(regex, x).groups())
                      for x in reversed(filenames)
                      if x.endswith('.bag')],
                     lambda x: x.name)
    orphans = []
    datasets = []
    for name, group in groups:
        group = list(group)
        bags = []
        prev_idx = None
        for bag in group:
            idx = bag.idx
            expected_idx = idx if prev_idx is None else prev_idx - 1
            if idx != expected_idx:
                orphans.extend(bags)
                bags[:] = []
            bags.insert(0, os.path.join(dirpath, bag.filename))
            prev_idx = idx
            if not idx:
                datasets.insert(0, DatasetInfo(name, bags))
                bags = []
        orphans.extend(bags)
    for orphan in sorted(orphans):
        log.warn("Orphaned bag '%s'", orphan)
    return datasets


@marv.node(Bagmeta)
@marv.input('dataset', marv_nodes.dataset)
def bagmeta(dataset):
    """Extract meta information from bag file.

    In case of multiple connections for one topic, they are assumed to
    be all of the same message type and either all be latching or none.

    A topic's message type and latching mode, and a message type's
    md5sum are assumed not to change across split bags.
    """
    dataset = yield marv.pull(dataset)
    paths = [x.path for x in dataset.files if x.path.endswith('.bag')]

    bags = []
    start_time = sys.maxint
    end_time = 0
    msg_types = {}
    topics = {}
    for path in paths:
        with rosbag.Bag(path) as bag:
            _start_time = int(bag.get_start_time() * 1.e9)
            _end_time = int(bag.get_end_time() * 1.e9)
            if _start_time < start_time:
                start_time = _start_time
            if _end_time > end_time:
                end_time = _end_time

            _msg_counts = defaultdict(int)
            for chunk in bag._chunks:
                for conid, count in chunk.connection_counts.iteritems():
                    _msg_counts[conid] += count

            _msg_types = {}
            _topics = {}
            for con in bag._connections.itervalues():
                _msg_type = {'name': con.datatype,
                             'md5sum': con.md5sum,
                             'msg_def': con.msg_def.strip()}
                if con.datatype not in _msg_types:
                    _msg_types[con.datatype] = _msg_type
                if con.datatype not in msg_types:
                    msg_types[con.datatype] = _msg_type
                else:
                    assert msg_types[con.datatype] == _msg_type

                assert con.id in _msg_counts  # defaultdict
                latching = {'0': False, '1': True}[con.header.get('latching', '0')]
                _topic = {'name': con.topic,
                          'msg_count': _msg_counts[con.id],
                          'msg_type': con.datatype,
                          'latching': latching}
                if con.topic not in _topics:
                    _topics[con.topic] = _topic
                if con.topic not in topics:
                    topics[con.topic] = _topic
                else:
                    topic = topics[con.topic]
                    topic['msg_count'] += _topic['msg_count']
                    assert topic['msg_type'] == _topic['msg_type']
                    assert topic['latching'] == _topic['latching']

            bags.append({
                'start_time': _start_time,
                'end_time': _end_time,
                'duration': _end_time - _start_time,
                'msg_count': sum(_msg_counts.itervalues()),
                'msg_types': _msg_types.values(),
                'topics': _topics.values(),
                'version': bag.version,
            })
    yield marv.push({
        'start_time': start_time,
        'end_time': end_time,
        'duration': end_time - start_time,
        'msg_count': sum(x['msg_count'] for x in bags),
        'msg_types': msg_types.values(),
        'topics': topics.values(),
        'bags': bags,
    })


def read_messages(paths, topics=None, start_time=None, end_time=None):
    """Iterate chronologically raw BagMessage for topic from paths."""
    bags = {path: rosbag.Bag(path) for path in paths}
    gens = {path: bag.read_messages(topics=topics, start_time=start_time,
                                    end_time=end_time, raw=True)
            for path, bag in bags.items()}
    msgs = {}
    prev_timestamp = genpy.Time(0)
    while True:
        for key in (gens.viewkeys() - msgs.viewkeys()):
            try:
                msgs[key] = gens[key].next()
            except StopIteration:
                bags[key].close()
                del bags[key]
                del gens[key]
        if not msgs:
            break
        next_key = reduce(lambda x, y: x if x[1].timestamp < y[1].timestamp else y,
                          msgs.items())[0]
        next_msg = msgs.pop(next_key)
        assert next_msg.timestamp >= prev_timestamp
        yield next_msg
        prev_timestamp = next_msg.timestamp


@marv.node(Message, Header, group='ondemand')
@marv.input('dataset', marv_nodes.dataset)
@marv.input('bagmeta', bagmeta)
def raw_messages(dataset, bagmeta):
    """Stream messages from a set of bag files."""
    bagmeta, dataset = yield marv.pull_all(bagmeta, dataset)
    bagtopics = {x.name: x for x in bagmeta.topics}
    paths = [x.path for x in dataset.files if x.path.endswith('.bag')]
    requested = yield marv.get_requested()

    alltopics = set()
    bytopic = defaultdict(list)
    groups = {}
    for name in [x.name for x in requested]:
        if ':' in name:
            reqtop, reqtype = name.split(':')
            topics = [topic.name for topic in bagmeta.topics
                      if ((reqtop == '*' or reqtop == topic.name) and
                          (reqtype == '*' or reqtype == topic.msg_type))]
            group = groups[name] = yield marv.create_group(name)
            create_stream = group.create_stream
        else:
            topics = [name] if name in bagtopics else []
            group = None
            create_stream = marv.create_stream

        for topic in topics:
            info = bagtopics[topic]
            # TODO: start/end_time per topic?
            header = {'start_time': bagmeta.start_time,
                      'end_time': bagmeta.end_time,
                      'msg_count': info.msg_count,
                      'msg_type': info.msg_type,
                      'topic': topic}
            stream = yield create_stream(topic, **header)
            bytopic[topic].append(stream)
        alltopics.update(topics)
        if group:
            yield group.finish()

    if not alltopics:
        return

    for topic, raw, t in read_messages(paths, topics=list(alltopics)):
        dct = {'data': raw[1], 'timestamp': t.to_nsec()}
        for stream in bytopic[topic]:
            yield stream.msg(dct)

messages = raw_messages
