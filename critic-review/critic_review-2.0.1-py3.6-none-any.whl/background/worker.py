# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2017 the Critic contributors, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import logging
import os
import pickle
import resource
import struct
import sys
import traceback

logger = logging.getLogger("background.worker")

class ForwardingHandler(logging.Handler):
    def __init__(self, stream):
        super(ForwardingHandler, self).__init__()
        self.stream = stream

    def emit(self, record):
        record.context = f"{record.name}[{os.getpid()}]"
        if record.exc_info:
            record.stacktrace = "\n" + "".join(
                traceback.format_exception(*record.exc_info)).strip()
            record.exc_info = None
        pickled = pickle.dumps(record, pickle.HIGHEST_PROTOCOL)
        sys.stderr.buffer.write(struct.pack("=I", len(pickled)) + pickled)

# def apply_limits(service_data):
#     if "rss_limit" in service_data:
#         rss_limit = service_data["rss_limit"]
#         logger.info("Applying RSS limit: %d", rss_limit)
#         soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_RSS)
#         if soft_limit < rss_limit:
#             resource.setrlimit(resource.RLIMIT_RSS, (rss_limit, hard_limit))

def call(fn, *args, **kwargs):
    handler = ForwardingHandler(sys.stderr)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    try:
        fn(*args, **kwargs)
    except Exception:
        logger.exception("Uncaught exception")
        sys.exit(1)
    else:
        sys.exit(0)
