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

import logging

logger = logging.getLogger("background.extensiontasks")

import api
import background
import extensions.role.filterhook

class ExtensionTasks(background.service.BackgroundService):
    name = "extensiontasks"

    def will_start(self):
        if not self.settings.extensions.enabled:
            logger.info("Extension support not enabled")
            return False
        return True

    async def did_start(self):
        self.__failed_events = set()

    async def wake_up(self):
        with api.critic.startSession(for_system=True) as critic:
            cursor = critic.getDatabaseCursor()
            cursor.execute("""SELECT id
                                FROM extensionfilterhookevents
                            ORDER BY id ASC""")

            finished_events = []

            for (event_id,) in cursor:
                if event_id not in self.__failed_events:
                    try:
                        extensions.role.filterhook.processFilterHookEvent(
                            critic.database, event_id, self.debug)
                    except Exception:
                        logger.exception("Failed to process filter hook event:")
                        self.__failed_events.add(event_id)
                    else:
                        finished_events.append(event_id)

            with critic.database.updating_cursor(
                    "extensionfilterhookevents") as cursor:
                cursor.execute("""DELETE FROM extensionfilterhookevents
                                        WHERE id=ANY (%s)""",
                               (finished_events,))

if __name__ == "__main__":
    background.service.call(ExtensionTasks)
