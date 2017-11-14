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
import logging

logger = logging.getLogger("background.extensionrunner")

import background
import extensions.execute

class ExtensionProcess():
    def __init__(self, process):
        self.process = process

class ExtensionRunner(background.service.BackgroundService):
    name = "extensionrunner"
    manage_socket = True

    def will_start(self):
        if not self.settings.extensions.enabled:
            logger.info("Extension support not enabled")
            return False
        return True

    async def did_start(self):
        self.__cached_processes = []
        self.__max_cached_processes = self.service_data["cached_processes"]

        asyncio.ensure_future(self.__fill_cache())

    async def __start_process(self, flavor):
        process_params = extensions.execute.get_process_params(flavor)
        return await asyncio.create_subprocess_exec(
            *process_params.argv, cwd=process_params["cwd"],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

    async def __fill_cache(self):
        while await self.__cache_process():
            pass

    async def __cache_process(self):
        if len(self.__cached_processes) < self.__max_cached_processes:
            process = await self.__start_process(
                self.settings.extensions.default_flavor)
            logger.debug("started cached process [pid=%d]" % process.pid)
            self.__cached_processes.append(process)
            return True
        else:
            return False

    async def get_extension_process(self, flavor):
        if flavor == self.settings.extensions.default_flavor:
            if self.__cached_processes:
                asyncio.ensure_future(self.__cache_process())
                return self.__cached_processes.pop(0)
        return await self.__start_process(flavor)

    async def handle_client_command(self, command):
        process = await self.get_extension_process(command["flavor"])

        try:
            stdout, stderr = asyncio.wait_for(process.commuicate(
                command["stdin_data"].encode()), command["timeout"])
        except asyncio.TimeoutError:
            logger.info(
                "Extension process timed out, killing [pid=%d", process.pid)
            process.kill()
            await process.wait()
            raise

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode("latin-1"),  # Used as "identity" codec
            "stderr": stderr.decode(),
        }

if __name__ == "__main__":
    background.service.call(ExtensionRunner)
