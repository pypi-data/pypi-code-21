# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2015 the Critic contributors, Opera Software ASA
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
import sys
import traceback

logger = logging.getLogger("background.reviewupdater")

import api
import dbutils
import gitutils
import background.utils
import mailutils

from .service import BackgroundService

def process_branchupdate(review, branchupdate_id, pendingrefupdate_id):
    critic = review.critic

    if pendingrefupdate_id is None:
        updater_id = None
    else:
        cursor = critic.getDatabaseCursor()
        cursor.execute("""SELECT updater
                            FROM pendingrefupdates
                           WHERE id=%s""",
                       (pendingrefupdate_id,))
        updater_id, = cursor.fetchone()

    result = {
        "status": "ok"
    }

    try:
        dbutils.Review.fromAPI(review).processBranchUpdate(
            critic.database, branchupdate_id, pendingrefupdate_id)

        next_state = 'finished'
    except dbutils.ReviewUpdateError as error:
        gitutils.emitGitHookOutput(
            critic.database, pendingrefupdate_id,
            # FIXME: Refine this error message.
            #output="An error occurred while updating the review.",
            output=traceback.format_exc(),
            error=str(error))

        if updater_id is not None:
            updater = dbutils.User.fromId(critic.database, updater_id)
            is_developer = updater.hasRole(critic.database, "developer")

            if not is_developer:
                summary = ("r/%d: processing branch update failed"
                           % review.id)
                mailutils.sendAdministratorErrorReport(
                    critic.database, "reviewupdater", summary, str(error))

        result.update({
            "status": "error",
            "error": str(error),
        })

        next_state = 'failed'

    with critic.database.updating_cursor("pendingrefupdates") as cursor:
        cursor.execute(
            """UPDATE pendingrefupdates
                  SET state=%s
                WHERE id=%s""",
            (next_state, pendingrefupdate_id))

    return result

def run_worker():
    data = json.load(sys.stdin)

    review_id = data["review_id"]
    branchupdate_id = data.get("branchupdate_id")
    pendingrefupdate_id = data.get("pendingrefupdate_id")

    with api.critic.startSession(for_system=True) as critic:
        review = api.review.fetch(critic, review_id)

        if branchupdate_id is not None:
            logger.debug("processing branch update: %d of r/%d",
                         branchupdate_id, review_id)

            result = process_branchupdate(
                review, branchupdate_id, pendingrefupdate_id)

    json.dump(result, sys.stdout)

class ReviewUpdater(BackgroundService):
    name = "reviewupdater"

    def __init__(self):
        super(ReviewUpdater, self).__init__()
        self.__processing = set()

    async def process_update(self, review_id, branchupdate_id,
                             pendingrefupdate_id):
        input_data = {
            "review_id": review_id,
            "branchupdate_id": branchupdate_id,
            "pendingrefupdate_id": pendingrefupdate_id
        }

        self.__processing.add(branchupdate_id)

        try:
            stdout = await self.run_worker(
                "background.reviewupdater", "--worker",
                stdin_data=json.dumps(input_data).encode())
        except background.service.WorkerError:
            logger.error(
                "Failed to process update: r/%d (branchupdate=%r)",
                review_id, branchupdate_id)
        else:
            self.__processing.remove(branchupdate_id)
            logger.info("Processed update: r/%d (branchupdate=%r)",
                        review_id, branchupdate_id)

    async def wake_up(self):
        logger.debug("woke up")

        with api.critic.startSession(for_system=True) as critic:
            cursor = critic.getDatabaseCursor()
            cursor.execute(
                """SELECT reviews.id, branchupdates.id, pendingrefupdates.id
                     FROM branchupdates
                     JOIN branches ON (branches.id=branchupdates.branch)
                     JOIN reviews ON (reviews.branch=branches.id)
          LEFT OUTER JOIN reviewupdates ON (reviewupdates.branchupdate=branchupdates.id)
          LEFT OUTER JOIN pendingrefupdates ON (pendingrefupdates.repository=branches.repository
                                            AND pendingrefupdates.name=('refs/heads/' || branches.name))
                    WHERE reviewupdates.review IS NULL
                      AND (pendingrefupdates.id IS NULL
                        OR pendingrefupdates.state='processed')""")

            for review_id, branchupdate_id, pendingrefupdate_id in cursor:
                if branchupdate_id not in self.__processing:
                    logger.debug(
                        "Processing update: r/%d (branchupdate=%d) ...",
                        review_id, branchupdate_id)

                    asyncio.ensure_future(self.process_update(
                        review_id, branchupdate_id, pendingrefupdate_id))

        logger.debug("going back to sleep")

if __name__ == "__main__":
    if "--worker" in sys.argv:
        background.worker.call(run_worker)
    else:
        background.service.call(ReviewUpdater)
