# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2013 Jens Lindström, Opera Software ASA
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

import asyncio
import json
import logging
import os
import shutil
import sys
import time
import traceback

logger = logging.getLogger("background.maintenance")

import api
import dbutils
import gitutils
import background

def run_git_gc(repository_id):
    with api.critic.startSession(for_system=True) as critic:
        with gitutils.Repository.fromId(
                critic.database, repository_id) as repository:
            logger.debug("repository GC: %s" % repository.name)
            repository.packKeepaliveRefs(critic)
            repository.run("gc", "--prune=1 day", "--quiet")

def run_worker():
    request = json.load(sys.stdin)
    run_git_gc(**request)
    json.dump({}, sys.stdout)

class MaintenanceService(background.service.BackgroundService):
    name = "maintenance"

    async def did_start(self):
        hours, _, minutes = self.service_data["run_at"].partition(":")
        self.register_maintenance(self.__maintenance, int(hours), int(minutes))

        with api.critic.startSession(for_system=True) as critic:
            # Do an initial load/update of timezones.
            #
            # The 'timezones' table initially (post-installation) only contains
            # the Universal/UTC timezone; this call adds all the others that the
            # PostgreSQL database server knows about.
            dbutils.loadTimezones(critic.database)

    async def __maintenance(self):
        with api.critic.startSession(for_system=True) as critic:
            cursor = critic.database.cursor()

            # Update the UTC offsets of all timezones.
            #
            # The PostgreSQL database server has accurate (DST-adjusted) values,
            # but is very slow to query, so we cache the UTC offsets in our
            # 'timezones' table.  This call updates that cache every night.
            # (This is obviously a no-op most nights, but we don't want to have
            # to care about which nights it isn't.)
            logger.debug("updating timezones")
            dbutils.updateTimezones(critic.database)

            await asyncio.sleep(0)

            # Execute scheduled review branch archivals.
            if self.settings.repositories.archive_review_branches:
                repository = None

                cursor.execute("""SELECT branches.repository, branches.id, branches.name
                                    FROM scheduledreviewbrancharchivals
                                    JOIN reviews ON (reviews.id=scheduledreviewbrancharchivals.review)
                                    JOIN branches ON (branches.id=reviews.branch)
                                   WHERE scheduledreviewbrancharchivals.deadline <= NOW()
                                     AND reviews.state IN ('closed', 'dropped')
                                     AND NOT branches.archived
                                ORDER BY branches.repository""",
                               for_update=True)

                for repository_id, branch_id, branch_name in cursor:
                    if not repository or repository.id != repository_id:
                        if repository:
                            repository.stopBatch()
                        repository = gitutils.Repository.fromId(
                            critic.database, repository_id)
                        logger.info("archiving branches in: " + repository.name)

                    logger.info("  " + branch_name)

                    branch = dbutils.Branch.fromId(
                        critic.database, branch_id, repository=repository)

                    try:
                        branch.archive(critic.database)
                    except Exception:
                        logger.warning(traceback.format_exc())

                    await asyncio.sleep(0)

                # Since NOW() returns the same value each time within a single
                # transaction, this is guaranteed to delete only the set of
                # archivals we selected above.
                cursor.execute("""DELETE
                                    FROM scheduledreviewbrancharchivals
                                   WHERE deadline <= NOW()""")

                critic.database.commit()

            await asyncio.sleep(0)

            # Run a garbage collect in all Git repositories, to keep them neat
            # and tidy.  Also pack keepalive refs.
            cursor.execute("SELECT id FROM repositories")
            for (repository_id,) in cursor:
                request = {"repository_id":repository_id}
                await self.run_worker(
                    stdin_data=json.dumps(request).encode())

            if self.settings.extensions.enabled:
                now = time.time()
                max_age = 7 * 24 * 60 * 60

                base_path = os.path.join(
                    self.settings.paths.home,
                    self.settings.extensions.workcopy_dir)

                for user_name in os.listdir(base_path):
                    user_dir = os.path.join(base_path, user_name)

                    for extension_id in os.listdir(user_dir):
                        extension_dir = os.path.join(user_dir, extension_id)

                        for repository_name in os.listdir(extension_dir):
                            repository_dir = os.path.join(extension_dir,
                                                          repository_name)
                            age = now - os.stat(repository_dir).st_mtime

                            if age > max_age:
                                logger.info("Removing repository work copy: %s",
                                            repository_dir)
                                shutil.rmtree(repository_dir)
                                await asyncio.sleep(0)

if __name__ == "__main__":
    if "--worker" in sys.argv:
        background.worker.call(run_worker)
    else:
        background.service.call(MaintenanceService)
