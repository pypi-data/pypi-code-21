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
import datetime
import re
import time
from typing import List, Dict

from kudubot.entities.Message import Message
from kudubot.services.HelperService import HelperService
from kudubot.services.native.reminder.database import initialize_database, \
    store_reminder, get_unsent_reminders, \
    mark_reminder_sent, convert_datetime_to_string
from itertools import ifilter


class ReminderService(HelperService):
    u"""
    Class that implements a Service for the Kudubot framework that allows
    users to store reminder message that are then sent at a later time
    """

    def init(self):
        u"""
        Initializes the database table and starts a background thread that
        perpetually searches for expired reminders
        """
        self.initialize_database_table(initializer=initialize_database)
        self.start_daemon_thread(self.background_loop)

    @staticmethod
    def define_requirements():
        u"""
        Defines the dependencies for the Service

        :return: A list of dependencies
        """
        return []

    @staticmethod
    def define_identifier():
        u"""
        Defines the identifier for this service

        :return: The Service's identifier
        """
        return u"reminder"

    def define_command_name(self, language):
        u"""
        Defines the command name for this service
        :param language: the language in which to get the command name
        :return: The command name in the specified language
        """
        return {u"en": u"/remind", u"de": u"/erinner"}[language]

    def define_language_text(self):
        u"""
        :return: A dictionary used to translate any user-facing messages
        """
        return {
            u"@remind_command": {u"en": u"/remind", u"de": u"/erinner"},
            u"@list_argument": {u"en": u"list", u"de": u"auflisten"},
            u"@second_singular": {u"en": u"second", u"de": u"sekunde"},
            u"@second_plural": {u"en": u"seconds", u"de": u"sekunden"},
            u"@minute_singular": {u"en": u"minute", u"de": u"minute"},
            u"@minute_plural": {u"en": u"minutes", u"de": u"minuten"},
            u"@hour_singular": {u"en": u"hour", u"de": u"stunde"},
            u"@hour_plural": {u"en": u"hours", u"de": u"stunden"},
            u"@day_singular": {u"en": u"day", u"de": u"tag"},
            u"@day_plural": {u"en": u"days", u"de": u"tage"},
            u"@week_singular": {u"en": u"week", u"de": u"woche"},
            u"@week_plural": {u"en": u"weeks", u"de": u"wochen"},
            u"@year_singular": {u"en": u"year", u"de": u"jahr"},
            u"@year_plural": {u"en": u"years", u"de": u"jahre"},
            u"@stored_reply_title": {
                u"en": u"Message Stored", u"de": u"Nachricht gespeichert"
            },
            u"@stored_confirmation_message": {
                u"en": u"The reminder message has successfully been stored.",
                u"de": u"Die Erinnerungsnachricht wurde erfolgreich gespeichert"
            },
            u"@list_stored_message_start": {
                u"en": u"The following reminders are pending",
                u"de": u"Die folgenden Erinnerungen stehen noch aus"
            },
            u"@list_response_title": {
                u"en": u"List of Reminders", u"de": u"Liste der Erinnerungen"
            },
            u"@invalid_title": {
                u"en": u"Invalid Reminder", u"de": u"Ungültige Erinnerung"
            },
            u"@invalid_message": {
                u"en": u"The reminder is invalid. "
                      u"Please consult /remind syntax for more information.",
                u"de": u"Die Erinnerung ist fehlerhaft."
                      u"Sehe dir die /erinner syntax an, "
                      u"und versuch es dann noch einmal."
            }
        }

    def handle_message(self, message):
        u"""
        Handles a message received by the Service

        :param message: The message to handle
        :return: None
        """
        target = message.get_direct_response_contact()
        command = self.parse_message(message.message_body.strip(),
                                     self.determine_language(message))

        if command[u"mode"] == u"store":
            store_reminder(self.connection.db,
                           command[u"data"][u"message"],
                           command[u"data"][u"due_time"],
                           target.database_id)
            self.reply_translated(u"@stored_reply_title",
                                  u"@stored_confirmation_message", message)

        elif command[u"mode"] == u"list":
            reminders = list(ifilter(
                lambda x: x[u"receiver"].database_id == target.database_id,
                get_unsent_reminders(self.connection.db)
            ))
            text = u"@list_stored_message_start:\n\n"
            for reminder in reminders:
                text += convert_datetime_to_string(reminder[u"due_time"])
                text += u":" + reminder[u"message"] + u"\n"
            self.reply_translated(u"@list_response_title", text, message)

        elif command[u"mode"] == u"invalid":
            self.reply_translated(
                u"@invalid_title", u"@invalid_message", message)

    def is_applicable_to(self, message):
        u"""
        Checks if the Service is applicable to a message

        :param message: The message to check
        :return: True if the Service is applicable, otherwise False
        """
        language = self.determine_language(message)
        body = message.message_body.lower().strip()

        regex = u"^@remind_command ([0-9]+ (" \
                u"@second_singular|@second_plural|@minute_singular|" \
                u"@minute_plural|@hour_singular|@hour_plural|" \
                u"@day_singular|@day_plural|@week_singular|@week_plural" \
                u"|@year_singular|@year_plural) )+" \
                u"\"[^\"]+\"$"
        lang_regex = re.compile(self.translate(regex, language))

        return re.match(lang_regex, body) \
            or body == self.translate(
                u"@remind_command @list_argument", language)

    def background_loop(self):
        u"""
        Perpetually checks for expiring reminders.

        :return: None
        """
        db = self.connection.get_database_connection_copy()
        while True:
            unsent = get_unsent_reminders(db)

            for reminder in unsent:

                due_time = reminder[u"due_time"].timestamp()
                now = datetime.datetime.utcnow().timestamp()
                if due_time < now:

                    self.connection.send_message(Message(
                        u"Reminder",
                        reminder[u"message"],
                        reminder[u"receiver"],
                        self.connection.user_contact)
                    )
                    mark_reminder_sent(db, reminder[u"id"])

            time.sleep(1)

    def define_syntax_description(self, language):
        u"""
        Defines the syntax with which the user can interact with this service

        :param language: The language to use
        :return: The syntax description in the specified language
        """
        return {
            u"en": u"Set a reminder:\n"
                  u"/remind X second(s) \"Message\"\n"
                  u"/remind X minute(s) \"Message\"\n"
                  u"/remind X hour(s) \"Message\"\n"
                  u"/remind X day(s) \"Message\"\n"
                  u"/remind X week(s) \"Message\"\n"
                  u"/remind X year(s) \"Message\"\n"
                  u"/remind tomorrow \"Message\"\n"
                  u"/remind next week \"Message\"\n"
                  u"/remind next year \"Message\"\n\n"
                  u"Combinations:\n"
                  u"/remind X hours Y minutes Z seconds \"Message\"\n\n"
                  u"List pending reminders:\n"
                  u"/remind list",
            u"de": u"Erinnerung setzen:\n"
                  u"/erinner X sekunde(n) \"Message\"\n"
                  u"/erinner X minute(n) \"Message\"\n"
                  u"/erinner X stunde(n) \"Message\"\n"
                  u"/erinner X tag(e) \"Message\"\n"
                  u"/erinner X woche(n) \"Message\"\n"
                  u"/erinner X jahr(e) \"Message\"\n"
                  u"/erinner morgen \"Message\"\n"
                  u"/erinner nächste woche \"Message\"\n"
                  u"/erinner nächstes jahr \"Message\"\n\n"
                  u"Kombinationen:\n"
                  u"/erinner X stunden Y minuten Z sekunden \"Message\"\n\n"
                  u"Gespeicherte Erinnerungen auflisten:\n"
                  u"/erinner auflisten"
        }[language]

    def determine_language(self, message):
        u"""
        Determines the language used in a message

        :param message: The message to analyse
        :return: The language that was found
        """

        if message.message_body.startswith(u"/erinner"):
            return u"de"
        else:
            return u"en"

    def define_help_message(self, language):
        u"""
        Defines the help message for this service in various languages

        :param language: The language to be used
        :return: The help description in the specified language
        """
        return {
            u"en": u"The reminder service allows you to store a reminder "
                  u"on the server to be sent back to you at a specified time. "
                  u"See /remind syntax for possible ways "
                  u"to use the reminder service.",
            u"de": u"Der Erinnerungsdienst erlaubt es einem Nutzer eine "
                  u"Erinnerung auf dem Server zu speichern, welcher dann zu"
                  u"einem spezifizierten Zeitpunkt zurückgesendet wird. "
                  u"Sehe dir /erinner syntax an, um dir ein Bild davon zu "
                  u"machen wie man den Erinnerungsdienst verwendet."
        }[language]

    def parse_message(self, text, language):
        u"""
        Parses the message and determines the mode of operation

        :param text: The text to parse
        :param language: The language in which to parse the text
        :return: A dictionary with at least the key 'status' with three
                 different possible states:
                 - no-match: The message does not match the command syntax
                 - help:     A query for the help message.
                             Will result in the help message being
                             sent to the sender
                 - store:    Command to store a new reminder
        """
        self.logger.debug(u"Parsing message")

        if self.translate(u"@remind_command @list_argument", language) \
                == text.lower():
            return {u"mode": u"list"}
        else:

            time_string = text.lower().split(u" \"")[0].split(
                self.translate(u"@remind_command ", language))[1]
            reminder_message = text.split(u"\"")[1]

            usertime = self.parse_time_string(time_string.strip(), language)

            if usertime is None:
                self.logger.debug(u"Invalid reminder message")
                return {u"mode": u"invalid"}
            else:
                self.logger.debug(u"Will store reminder")
                return {
                    u"mode": u"store",
                    u"data": {
                        u"message": reminder_message,
                        u"due_time": usertime
                    }
                }

    def parse_time_string(self, time_string, language):
        u"""
        Parses a time string like '1 week' or '2 weeks 1 day' etc. and returns
        a datetime object with the specified time difference to the current
        time.

        :param time_string: The time string to parse
        :param language: In which language the string should be parsed
        :return: The parsed datetime object or None in case the parsing failed
        """

        # turn all units into english singular units
        for unit in [u"second", u"minute", u"hour", u"day", u"week", u"year"]:

            # The order is very important here!
            for mode in [u"plural", u"singular"]:

                key = u"@" + unit + u"_" + mode
                text = self.translate(key, language)
                time_string = time_string.replace(text, unit)

        now = datetime.datetime.utcnow()
        parsed = time_string.split(u" ")

        try:
            for i in xrange(0, len(parsed), 2):

                value = int(parsed[i])
                key = parsed[i + 1]

                if key == u"year":
                    now += datetime.timedelta(days=value * 365)
                elif key == u"week":
                    now += datetime.timedelta(weeks=value)
                elif key == u"day":
                    now += datetime.timedelta(days=value)
                elif key == u"hour":
                    now += datetime.timedelta(hours=value)
                elif key == u"minute":
                    now += datetime.timedelta(minutes=value)
                elif key == u"second":
                    now += datetime.timedelta(seconds=value)
                else:
                    self.logger.debug(u"Invalid time keyword " + key + u" used")
                    return None

            return now

        # Datetime exception, too high date values
        except (ValueError, OverflowError):
            return None
