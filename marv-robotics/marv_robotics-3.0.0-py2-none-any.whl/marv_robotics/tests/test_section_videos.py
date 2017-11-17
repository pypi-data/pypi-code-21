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

import marv_node.testing
from marv_node.testing import make_dataset, make_sink, run_nodes, temporary_directory
from marv_nodes import SetID
from marv_store import Store
from pkg_resources import resource_filename

from marv_robotics.cam import ffmpeg
from marv_robotics.detail import video_section as node


PERSIST = {ffmpeg.name: ffmpeg}


class TestCase(marv_node.testing.TestCase):
    # TODO: Generate bags instead, but with connection info!
    BAGS = [resource_filename('marv_robotics.tests', 'data/cam.bag')]

    def test_node(self):
        with temporary_directory() as storedir:
            store = Store(storedir, PERSIST)
            dataset = make_dataset(self.BAGS)
            store.add_dataset(dataset)
            sink = make_sink(node)
            run_nodes(dataset, [sink], store, PERSIST)
            self.assertNodeOutput(sink.stream, node)
            # XXX: test also header
