# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
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

import sys
import os
import time
import json
import multiprocessing
import logging

logger = logging.getLogger("background.highlight")

import background
import gitutils
import syntaxhighlight
import syntaxhighlight.generate

def run_worker():
    request = json.load(sys.stdin)
    gitutils.GIT_EXECUTABLE = request.pop("git_executable")
    syntaxhighlight.CACHE_PATH = request.pop("cache_path")
    request["highlighted"] = syntaxhighlight.generate.generateHighlight(
        **request)
    json.dump(request, sys.stdout)

class HighlightService(background.service.BackgroundService):
    name = "highlight"
    manage_socket = True
    default_max_workers = multiprocessing.cpu_count()

    async def did_start(self):
        if "compact_at" in self.service_data:
            hours, _, minutes = self.service_data["compact_at"].partition(":")
            self.register_maintenance(self.compact, int(hours), int(minutes))

    async def will_run_worker(self, request):
        if syntaxhighlight.isHighlighted(
                request["sha1"], request["language"], request["mode"]):
            response = dict(request)
            response["highlighted"] = True
            return response
        request["default_encodings"] = self.settings.content.default_encodings
        request["git_executable"] = gitutils.git()
        request["cache_path"] = self.settings.paths.cache

    async def compact(self):
        pass

if __name__ == "__main__":
    if "--worker" in sys.argv:
        background.worker.call(run_worker)
    else:
        background.service.call(HighlightService)
