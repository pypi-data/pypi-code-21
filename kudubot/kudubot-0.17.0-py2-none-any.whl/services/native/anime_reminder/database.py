u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import
import logging
import sqlite3
from typing import List, Dict
from itertools import ifilter


logger = logging.getLogger(__name__)
u"""
The logger for this module
"""


# noinspection SqlNoDataSourceInspection,SqlDialectInspection
def initialize_database(db):
    u"""
    Initializes the Service's database tables

    :return: None
    """
    logger.info(u"Initializing Anime Reminder Database")

    db.execute(u"CREATE TABLE IF NOT EXISTS anime_reminder_subscriptions ("
               u"    id INTEGER CONSTRAINT constraint_name PRIMARY KEY,"
               u"    user_id INTEGER NOT NULL,"
               u"    show_name VARCHAR(255) NOT NULL"
               u")")
    db.execute(u"CREATE TABLE IF NOT EXISTS anime_reminder_threads ("
               u"    id INTEGER CONSTRAINT constraint_name PRIMARY KEY,"
               u"    show_name VARCHAR(255) NOT NULL,"
               u"    episode INTEGER NOT NULL,"
               u"    thread VARCHAR(255) NOT NULL"
               u")")
    db.commit()


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
def subscription_exists(user, show_name, db):
    u"""
    Checks if a subscription already exists

    :param user: The user ID for this subscription
    :param show_name: The show name of the subscription
    :param db: The database to use
    :return: True if the subscription already exists, otherwise False
    """
    subscriptions = ifilter(
        lambda x: x[u"show_name"].lower() == show_name.lower(),
        get_subscriptions(db, user)
    )
    return len(list(subscriptions)) >= 1


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
def store_subscription(user, show_name, db):
    u"""
    Creates a new subscription if it does not exist yet

    :param user: The user ID for this subscription
    :param show_name: The show name of the subscription
    :param db: The database to use
    :return: True if a new subscription was stored,
             False if the subscription already existed
    """
    exists = subscription_exists(user, show_name, db)

    if not exists:
        logger.debug(u"Creating new subscription for user " + unicode(user) +
                     u" and show " + show_name)
        db.execute(u"INSERT INTO anime_reminder_subscriptions "
                   u"(user_id, show_name) VALUES (?, ?)", (user, show_name))
        db.commit()
    else:
        logger.debug(u"Subscription for user " + unicode(user) + u" and show " +
                     show_name + u" already exists")

    return not exists


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
def delete_subscription(user, show_name, db):
    u"""
    Deletes a subscription from the database

    :param user: The user ID for this subscription
    :param show_name: The show name of the subscription
    :param db: The database to use
    :return True if the subscription existed and is deleted,
            False if the subscription did not exist beforehand
    """
    exists = subscription_exists(user, show_name, db)

    if exists:
        logger.debug(u"Deleting subscription for user " + unicode(user) +
                     u" and show " + show_name)
        db.execute(u"DELETE FROM anime_reminder_subscriptions "
                   u"WHERE user_id=? AND show_name LIKE ?",
                   (user, show_name))
        db.commit()
    else:
        logger.debug(u"Subscription for user " + unicode(user) + u" and show " +
                     show_name + u" did not exist. Not deleting anything.")

    return exists


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
def get_subscriptions(db, user=-1):
    u"""
    Fetches a list of subscriptions from the database, either for all users or
    one specific user.

    :param db: The database to use
    :param user: The user parameter can limit the query to search for
                 subscriptions for only one user
    :return: A list of dictionaries representing the subscriptions
    """

    if user == -1:
        subs = db.execute(u"SELECT id, user_id, show_name "
                          u"FROM anime_reminder_subscriptions").fetchall()

    else:
        subs = db.execute(u"SELECT id, user_id, show_name "
                          u"FROM anime_reminder_subscriptions "
                          u"WHERE user_id=?", (user,)).fetchall()

    formatted_subs = []
    for sub in subs:
        formatted_subs.append({
            u"id": sub[0], u"user_id": sub[1], u"show_name": sub[2]
        })

    return formatted_subs


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
def thread_exists(thread, db):
    u"""
    Checks if a reddit discussion thread with the given thread parameters
    already exists

    :param thread: The thread to check for
    :param db: The database to check
    :return: True if the thread exists, false otherwise
    """
    result = db.execute(
        u"SELECT * FROM anime_reminder_threads "
        u"WHERE show_name=? AND episode=? AND thread=?",
        (thread[u"show_name"], thread[u"episode"], thread[u"url"])
    )
    return len(result.fetchall()) > 0


# noinspection SqlNoDataSourceInspection,SqlDialectInspection,SqlResolve
def store_thread(thread, db):
    u"""
    Stores a reddit discussion thread in the database

    :param thread: The thread to store
    :param db: The database to use
    :return: None
    """
    logger.debug(u"Storing reddit thread " + unicode(thread))
    db.execute(
        u"INSERT INTO anime_reminder_threads (show_name, episode, thread) "
        u"VALUES (?, ?, ?)",
        (thread[u"show_name"], thread[u"episode"], thread[u"url"])
    )
    db.commit()
