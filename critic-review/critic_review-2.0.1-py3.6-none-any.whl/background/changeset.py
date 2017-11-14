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

import json
import logging
import multiprocessing
import os
import sys

logger = logging.getLogger("background.changeset")

import api
import background
import base

from changeset.create import createChangeset

def describe_request(request):
    if request["changeset_type"] in ("direct", "merge", "conflicts"):
        return "%s (%s)" % (request["changeset_type"],
                            request["child_sha1"][:8])
    return "custom (%s..%s)" % (request["parent_sha1"][:8],
                                request["child_sha1"][:8])

def run_worker():
    request = json.load(sys.stdin)

    logger.debug("generating changeset: %s", describe_request(request))

    with api.critic.startSession(for_system=True) as critic:
        createChangeset(critic.database, request)

    logger.info("Generated changeset: %s", describe_request(request))

    json.dump(request, sys.stdout)

class ChangesetService(background.service.BackgroundService):
    name = "changeset"
    manage_socket = True
    default_max_workers = max(1, multiprocessing.cpu_count() // 2)

    async def did_start(self):
        if "purge_at" in self.service_data:
            hours, _, minutes = self.service_data["purge_at"].partition(":")
            self.register_maintenance(self.purge, int(hours), int(minutes))

    async def purge(self):
        if base.configuration()["database.driver"] != "postgresql":
            # The "INTERVAL '3 months'" syntax used below is not supported by
            # SQLite. Also, it's highly unlikely that a quickstarted instance
            # is used beyond 3 months, rendering this code pretty useless.
            return

        with api.critic.startSession(for_system=True) as critic:
            db = critic.database

            cursor = db.readonly_cursor()
            cursor.execute(
                """SELECT COUNT(*)
                     FROM changesets
                     JOIN customchangesets
                          ON (customchangesets.changeset=changesets.id)
                    WHERE time < NOW() - INTERVAL '3 months'""")
        npurged = cursor.fetchone()[0]

        if npurged:
            logger.info("Purging %d custom changesets" % npurged)

            with db.updating_cursor("changesets") as cursor:
                cursor.execute(
                    """DELETE
                         FROM changesets
                        WHERE id IN (
                         SELECT changeset
                           FROM customchangesets
                          WHERE time < NOW() - INTERVAL '3 months')""")

if __name__ == "__main__":
    if "--worker" in sys.argv:
        background.worker.call(run_worker)
    else:
        background.service.call(ChangesetService)
