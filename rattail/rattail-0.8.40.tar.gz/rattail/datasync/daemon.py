# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
DataSync for Linux
"""

from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import time
import datetime
import logging
from traceback import format_exception

from rattail.db import api
from rattail.daemon import Daemon
from rattail.threads import Thread
from rattail.datasync.config import load_profiles
from rattail.mail import send_email
from rattail.time import make_utc


log = logging.getLogger(__name__)


class DataSyncDaemon(Daemon):
    """
    Linux daemon implementation of DataSync.
    """

    def run(self):
        """
        Starts watcher and consumer threads according to configuration.
        """
        for key, profile in load_profiles(self.config).iteritems():

            # Create watcher thread for the profile.
            name = '{0}-watcher'.format(key)
            log.debug("starting thread '{0}' with watcher: {1}".format(name, profile.watcher_spec))
            thread = Thread(target=watch_for_changes, name=name, args=(self.config, profile.watcher))
            thread.daemon = True
            thread.start()

            # Create consumer threads, unless watcher consumes itself.
            if not profile.watcher.consumes_self:

                # Create a thread for each "isolated" consumer.
                for consumer in profile.isolated_consumers:
                    name = '{0}-consumer-{1}'.format(key, consumer.key)
                    log.debug("starting thread '{0}' with isolated consumer: {1}".format(name, consumer.spec))
                    thread = Thread(target=consume_changes, name=name, args=(profile, [consumer]))
                    thread.daemon = True
                    thread.start()

                # Maybe create a common (shared transaction) thread for the rest of
                # the consumers.
                if profile.common_consumers:
                    name = '{0}-consumer-shared'.format(key)
                    log.debug("starting thread '{0}' with consumer(s): {1}".format(
                        name, ','.join(["{0} ({1})".format(c.key, c.spec) for c in profile.common_consumers])))
                    thread = Thread(target=consume_changes, name=name, args=(profile, profile.common_consumers,))
                    thread.daemon = True
                    thread.start()

        # Loop indefinitely.  Since this is the main thread, the app will
        # terminate when this method ends; all other threads are "subservient"
        # to this one.
        while True:
            time.sleep(.01)


def watch_for_changes(config, watcher):
    """
    Target for DataSync watcher threads.
    """
    # Let watcher do any setup it needs.
    watcher.setup()

    # The 'last run' value is maintained as zone-aware UTC.
    timefmt = '%Y-%m-%d %H:%M:%S'
    lastrun_setting = 'rattail.datasync.{}.watcher.lastrun'.format(watcher.key)
    lastrun = api.get_setting(None, lastrun_setting)
    if lastrun:
        lastrun = datetime.datetime.strptime(lastrun, timefmt)
        lastrun = make_utc(lastrun, tzinfo=True)

    while True:

        thisrun = make_utc(tzinfo=True)
        attempts = 0
        errtype = None
        while True:

            attempts += 1

            try:
                changes = watcher.get_changes(lastrun)

            except Exception as error:

                exc_type, exc, traceback = sys.exc_info()

                # If we've reached our final attempt, stop retrying.
                if attempts >= watcher.retry_attempts:
                    log.warning("attempt #{} failed calling `watcher.get_changes()`, this thread "
                                "will now *terminate* until datasync restart".format(attempts),
                                exc_info=True)
                    send_email(config, 'datasync_error_watcher_get_changes', {
                        'watcher': watcher,
                        'error': exc,
                        'attempts': attempts,
                        'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
                        'datasync_url': config.datasync_url(),
                    })
                    raise

                # If this exception is not the first, and is of a different type
                # than seen previously, do *not* continue to retry.
                if errtype is not None and not isinstance(error, errtype):
                    log.exception("new exception differs from previous one(s), "
                                  "giving up on watcher.get_changes()")
                    raise

                # Record the type of exception seen, and pause for next retry.
                errtype = type(error)
                log.warning("attempt #{} failed for '{}' watcher.get_changes()".format(attempts, watcher.key))
                log.debug("pausing for {} seconds before making attempt #{} of {}".format(
                    watcher.retry_delay, attempts + 1, watcher.retry_attempts))
                if watcher.retry_delay:
                    time.sleep(watcher.retry_delay)

            else:
                # watcher got changes okay, so record/process and prune, then
                # break out of inner loop to reset the attempt count for next grab
                lastrun = thisrun
                api.save_setting(None, lastrun_setting, lastrun.strftime(timefmt))
                if changes:
                    log.debug("got {} changes from '{}' watcher".format(len(changes), watcher.key))
                    # TODO: and what if this step fails..??
                    if record_or_process_changes(watcher, changes):
                        prune_changes(watcher, changes)
                break

        # sleep a moment between successful change grabs
        time.sleep(watcher.delay)


def record_or_process_changes(watcher, changes):
    """
    Now that we have changes from the watcher, we'll either record them as
    proper DataSync changes, or else let the watcher process them (if it
    consumes self).
    """
    from rattail.db import Session, model

    # If watcher consumes itself, then it will process its own changes.  Note
    # that there are no assumptions made about the format or structure of these
    # change objects.
    if watcher.consumes_self:
        session = Session()
        try:
            watcher.process_changes(session, changes)
        except Exception:
            log.exception("error calling watcher.process_changes()")
            session.rollback()
            raise
        else:
            session.commit()
            log.debug("watcher has consumed its own changes")
            return True
        finally:
            session.close()

    else:
        # Give all change stubs the same timestamp, to help identify them
        # as a "batch" of sorts, so consumers can process them as such.
        now = datetime.datetime.utcnow()

        # Save change stub records to rattail database, for consumer thread
        # to find and process.
        saved = 0
        session = Session()
        for key, change in changes:
            for consumer in watcher.consumer_stub_keys:
                session.add(model.DataSyncChange(
                    source=watcher.key,
                    payload_type=change.payload_type,
                    payload_key=change.payload_key,
                    deletion=change.deletion,
                    obtained=now,
                    consumer=consumer))
                saved += 1
            session.flush()
        session.commit()
        session.close()
        log.debug("saved {} '{}' changes to datasync queue".format(saved, watcher.key))
        return True


def prune_changes(watcher, changes):
    """
    Tell the watcher to prune the original change records from its source
    database, if relevant.
    """
    if watcher.prunes_changes:
        try:
            # Note that we only give it the keys for this.
            pruned = watcher.prune_changes([c[0] for c in changes])
        except:
            log.exception("error calling watcher.prune_changes()")
            raise
        else:
            if pruned is not None:
                log.debug("pruned {} changes from '{}' database".format(pruned, watcher.key))


def consume_changes(profile, consumers):
    """
    Target for DataSync consumer thread.
    """
    from rattail.db import Session, model

    # Let consumers do any setup they need.
    for consumer in consumers:
        consumer.setup()

    def process(session, consumer, changes):
        try:
            consumer.process_changes(session, changes)
            session.flush()
        except:
            log.exception("error calling consumer.process_changes(), this consumer "
                          "will now *terminate* (until datasync is restarted)")
            return False
        for change in changes:
            session.delete(change)
            session.flush()
        return True

    error = False
    while True:

        session = Session()
        for consumer in consumers:

            changes = session.query(model.DataSyncChange)\
                             .filter(model.DataSyncChange.source == profile.key)\
                             .filter(model.DataSyncChange.consumer == consumer.key)\
                             .order_by(model.DataSyncChange.obtained)\
                             .all()
                
            if changes:
                log.debug("found {} changes to process".format(len(changes)))
                consumer.begin_transaction()

                # Process (consume) changes in batches, according to timestamp.
                batch = []
                batchcount = 1
                changecount = 0
                timestamp = None
                for change in changes:
                    if timestamp and change.obtained != timestamp:
                        if process(session, consumer, batch):
                            changecount += len(batch)
                        else:
                            error = True
                            break
                        batch = []
                        batchcount += 1
                    batch.append(change)
                    timestamp = change.obtained
                if not error:
                    if process(session, consumer, batch):
                        changecount += len(batch)
                    else:
                        error = True

                log.debug("processed {} changes in {} batches{}".format(
                    changecount, batchcount, " (with errors)" if error else ""))
                if error:
                    consumer.rollback_transaction()
                    break
                else:
                    consumer.commit_transaction()

        if error:
            session.rollback()
            session.close()
            break
        else:
            session.commit()
            session.close()

        time.sleep(profile.consumer_delay)
