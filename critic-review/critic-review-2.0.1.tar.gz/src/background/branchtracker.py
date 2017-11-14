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

import asyncio
import functools
import json
import logging
import sys
import traceback

logger = logging.getLogger("background.branchtracker")

import api
import background
import dbutils
import gitutils
import mailutils

# Git (git-send-pack) appends a line suffix to its output.  This suffix depends
# on the $TERM value.  When $TERM is "dumb", the suffix is 8 spaces.  We strip
# this suffix if it's present.  (If we incorrectly strip 8 spaces not actually
# added by Git, it's not the end of the world.)
#
# See https://github.com/git/git/blob/master/sideband.c for details.
DUMB_SUFFIX = "        "

def perform_update(critic, *, trackedbranch_id, repository_id, local_name,
                   remote, remote_name, forced):
    def insert_log(from_sha1, to_sha1, hook_output, successful):
        if from_sha1 is None:
            from_sha1 = "0" * 40
        if to_sha1 is None:
            to_sha1 = "0" * 40
        with critic.database.updating_cursor("trackedbranchlog") as cursor:
            cursor.execute(
                """INSERT
                     INTO trackedbranchlog (branch, from_sha1, to_sha1,
                                            hook_output, successful)
                   VALUES (%s, %s, %s, %s, %s)""",
                (trackedbranch_id, from_sha1, to_sha1, hook_output, successful))

    def send_error_mail(hook_output):
        cursor = critic.getDatabaseCursor()
        cursor.execute("""SELECT uid
                            FROM trackedbranchusers
                           WHERE branch=%s""",
                       (trackedbranch_id,))

        recipients = [dbutils.User.fromId(critic.database, user_id)
                      for (user_id,) in cursor]

        if local_name == "*":
            subject = (f"{repository.name}: update of tags from {remote} "
                       "stopped!")
            body = f"""\
The automatic update of tags in
  {critic.settings.system.hostname}:{repository.path}
from the remote
  {remote}
failed, and has been disabled.  Manual intervention is required to resume the
automatic updating."""
        else:
            subject = (f"{local_name}: update from {remote_name} in {remote} "
                       "stopped!")
            body = f"""\
The automatic update of the branch '{local_name}' in
  {critic.settings.system.hostname}:{repository.path}
from the branch '{remote_name}' in
  {remote}
failed, and has been disabled.  Manual intervention is required to resume the
automatic updating."""

        if hook_output:
            body += """

Output from Critic's git hook
-----------------------------

{hook_output}"""

        mailutils.sendMessage(critic.database, recipients, subject, body)

    def disable_tracking():
        with critic.database.updating_cursor("trackedbranches") as cursor:
            cursor.execute("""UPDATE trackedbranches
                                 SET disabled=TRUE
                               WHERE id=%s""",
                           (trackedbranch_id,))
        logger.info("Tracking disabled")

    def finish():
        with critic.database.updating_cursor("trackedbranches") as cursor:
            cursor.execute("""UPDATE trackedbranches
                                 SET updating=FALSE
                               WHERE id=%s""",
                           (trackedbranch_id,))
        logger.info("Update finished")

    repository = gitutils.Repository.fromId(critic.database, repository_id)

    if local_name == "*":
        logger.debug("checking tags in %s", remote)
    else:
        logger.debug("checking %s in %s", remote_name, remote)

    try:
        with repository.relaycopy("branchtracker") as relay:
            current = None
            new = None
            tags = []

            if local_name == "*":
                output = relay.run("fetch", remote, "refs/tags/*:refs/tags/*",
                                   include_stderr=True)
                for line in output.splitlines():
                    if "[new tag]" in line:
                        tags.append(line.rsplit(" ", 1)[-1])
            else:
                relay.run("fetch", "--quiet", "--no-tags", remote,
                          f"refs/heads/{remote_name}")
                try:
                    current = repository.revparse(f"refs/heads/{local_name}")
                except gitutils.GitReferenceError:
                    # It's okay if the local branch doesn't exist (yet).
                    current = None
                new = relay.run("rev-parse", "FETCH_HEAD").strip()

            if current != new or tags:
                if local_name == "*":
                    refspecs = [f"refs/tags/{tag}" for tag in tags]
                else:
                    refspecs = [f"FETCH_HEAD:refs/heads/{local_name}"]

                flags = json.dumps({"trackedbranch_id": trackedbranch_id})

                returncode, stdout, stderr = relay.run(
                    "push", "--force", "origin", *refspecs,
                    env={"CRITIC_FLAGS": flags, "TERM": "dumb"},
                    check_errors=False)

                stderr_lines = []
                remote_lines = []

                for line in stderr.splitlines():
                    if line.endswith(DUMB_SUFFIX):
                        line = line[:-len(DUMB_SUFFIX)]
                    stderr_lines.append(line)
                    if line.startswith("remote: "):
                        line = line[8:]
                        remote_lines.append(line)

                if returncode == 0:
                    if local_name == "*":
                        for tag in tags:
                            logger.info("  updated tag: %s", tag)
                    elif current:
                        logger.info("  updated branch: %s: %s..%s",
                                    local_name, current[:8], new[:8])
                    else:
                        logger.info("  created branch: %s: %s",
                                    local_name, new[:8])

                    hook_output = ""

                    for line in remote_lines:
                        logger.debug("  [hook] %s", line)
                        hook_output += line + "\n"

                    if local_name != "*":
                        insert_log(current, new, hook_output, True)
                else:
                    if local_name == "*":
                        error = f"update of tags from {remote} failed"
                    else:
                        error = (f"update of branch {local_name} from "
                                 f"{remote_name} in {remote} failed")

                    hook_output = ""

                    for line in stderr_lines:
                        error += "\n    " + line

                    for line in remote_lines:
                        hook_output += line + "\n"

                    logger.error(error)

                    if local_name != "*":
                        insert_log(current, new, hook_output, False)

                    send_error_mail(hook_output)
                    disable_tracking()
            else:
                logger.debug("  fetched %s in %s; no changes",
                             remote_name, remote)

            finish()
    except Exception:
        exception = traceback.format_exc()

        if local_name == "*":
            error = f"  update of tags from {remote} failed"
        else:
            error = (f"  update of branch {local_name} from {remote_name} in "
                     f"{remote} failed")

        for line in exception.splitlines():
            error += "\n    " + line

        logger.error(error)

        # The expected failure (in case of diverged branches, or review branch
        # irregularities) is a failed "git push" and is handled above.  This is
        # an unexpected failure, so might be intermittent.  Leave the tracking
        # enabled and spam the system administrator(s).
        finish()

def run_worker():
    with api.critic.startSession(for_system=True) as critic:
        perform_update(critic, **json.load(sys.stdin))

class BranchTrackerService(background.service.BackgroundService):
    name = "branchtracker"

    def update_done(self, trackedbranch_id, task):
        self.__processing.remove(trackedbranch_id)
        self.loop.call_soon(self.do_wake_up)

    async def did_start(self):
        self.__processing = set()

    async def wake_up(self):
        with api.critic.startSession(for_system=True) as critic:
            cursor = critic.getDatabaseCursor()
            cursor.execute(
                """SELECT id, repository, local_name, remote, remote_name,
                          forced
                     FROM trackedbranches
                    WHERE NOT disabled
                      AND (next IS NULL OR next < NOW())
                 ORDER BY next ASC NULLS FIRST""")

            for (trackedbranch_id, repository_id, local_name,
                 remote, remote_name, forced) in cursor:
                request = {
                    "trackedbranch_id": trackedbranch_id,
                    "repository_id": repository_id,
                    "local_name": local_name,
                    "remote": remote,
                    "remote_name": remote_name,
                    "forced": forced
                }

                task = asyncio.ensure_future(self.run_worker(
                    stdin_data=json.dumps(request).encode()))
                task.add_done_callback(functools.partial(
                    self.update_done, trackedbranch_id))

                self.__processing.add(trackedbranch_id)

            cursor.execute(
                """SELECT COUNT(*), EXTRACT('epoch' FROM (MIN(next) - NOW()))
                     FROM trackedbranches
                    WHERE NOT disabled
                      AND NOT id=ANY (%s)""",
                (list(self.__processing),))

            pending_branches, update_delay = cursor.fetchone()

            with critic.database.updating_cursor("trackedbranches") as cursor:
                cursor.execute(
                    """UPDATE trackedbranches
                          SET previous=NOW(),
                              next=NOW() + delay
                        WHERE id=ANY (%s)""",
                    (list(self.__processing),))

            return update_delay if pending_branches else None

if __name__ == "__main__":
    if "--worker" in sys.argv:
        background.worker.call(run_worker)
    else:
        background.service.call(BranchTrackerService)
