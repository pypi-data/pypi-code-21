#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


import asyncio
import datetime
import itertools
import logging
import logging.handlers
import sys
import time

import turberfield.dialogue.cli
from turberfield.dialogue.directives import Pathfinder
from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.types import Player
from turberfield.utils.misc import gather_installed
from turberfield.utils.misc import log_setup

__doc__ = """
Script viewer.

Example:

python -m turberfield.dialogue.viewer \
--sequence=turberfield.dialogue.sequences.battle_royal:folder \
--ensemble=turberfield.dialogue.sequences.battle_royal.types:ensemble

"""

# TODO: add async_consumer and async_producer

async def view(queue, log=None, loop=None):
    log = log or logging.getLogger("turberfield.dialogue.view")
    loop = loop or ayncio.get_event_loop()
    prev = None
    while True:
        try:
            shot, item = await queue.get()
        except TypeError as e:
            log.debug("Got sentinel.")
            queue.task_done()
            prev = None
            return

        if prev and shot is not prev:
            log.info("Pause...")
            time.sleep(2)
            clear_screen()

        if isinstance(item, Model.Line):
            turberfield.dialogue.cli.line(shot, item)
            time.sleep(turberfield.dialogue.cli.pause(shot, item))

        prev = shot
        queue.task_done()

async def run_through(folder, ensemble, queue, log=None, loop=None):
    log = log or logging.getLogger("turberfield.dialogue.run_through")
    loop = loop or ayncio.get_event_loop()
    scripts = SceneScript.scripts(**folder._asdict())
    for script, interlude in itertools.zip_longest(
        scripts, itertools.cycle(folder.interludes)
    ):
        then = datetime.datetime.now()
        with script as dialogue:
            try:
                model = dialogue.cast(dialogue.select(ensemble, roles=1)).run()
            except (AttributeError, ValueError) as e:
                log.error(". ".join(getattr(e, "args", e) or e))
                return

            for n, (shot, item) in enumerate(model):
                await queue.put((shot, item))
                await queue.join()

                if isinstance(item, Model.Property):
                    log.info("Assigning {val} to {object}.{attr}".format(**item._asdict()))
                    setattr(item.object, item.attr, item.val)
                elif isinstance(item, Model.Audio):
                    log.info("Launnch {resource} from {package}.".format(**item._asdict()))
                elif isinstance(item, Model.Memory):
                    log.info("{subject} {state} {object}; {text}".format(**item._asdict()))
                    pass

        log.info("Time: {0}".format(datetime.datetime.now() - then))
        if interlude is None:
            rv = folder
        else:
            rv = await interlude(folder, ensemble, log=log, loop=loop)

        if rv is not folder:
            log.info("Interlude branching to {0}".format(rv))
            return rv

    await queue.put(None)
    return None

def main(args):
    loop = asyncio.get_event_loop()
    logName = log_setup(args, loop=loop)
    log = logging.getLogger(logName)

    if args.sequence and args.ensemble:
        folder = Pathfinder.string_import(
            args.sequence, relative=False, sep=":"
        )
        ensemble = Pathfinder.string_import(
            args.ensemble, relative=False, sep=":"
        )
    else:
        folder = turberfield.dialogue.cli.seq_menu(log)
        ensemble = turberfield.dialogue.cli.ensemble_menu(log)

    queue = asyncio.Queue(maxsize=1, loop=loop)
    projectionist = loop.create_task(view(queue, loop=loop))
    start = datetime.datetime.now()

    try:
        while folder:
            folder = loop.run_until_complete(
                run_through(folder, ensemble, queue, loop=loop)
            )
        else:
            log.info("Playing time: {0}".format(
                datetime.datetime.now() - start)
            )
    finally:
        queue.put_nowait(None)
        projectionist.cancel()
        loop.close()

    return 0

def run():
    p = turberfield.dialogue.cli.parser()
    p.add_argument(
        "--ensemble", default=None,
        help="Give an import path to a list of Personas."
    )
    p.add_argument(
        "--sequence", default=None,
        help="Give an import path to a SceneScript folder."
    )
    args = p.parse_args()
    if args.version:
        sys.stdout.write(turberfield.dialogue.__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
