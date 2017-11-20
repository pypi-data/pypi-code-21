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
import re
import time
import requests
from typing import List, Dict
from kudubot.entities.Message import Message
from kudubot.services.HelperService import HelperService
from kudubot.services.native.anime_reminder.scraper import \
    scrape_reddit_discussion_threads
from kudubot.services.native.anime_reminder.database import \
    initialize_database, store_subscription, delete_subscription, \
    get_subscriptions, thread_exists, store_thread


class AnimeReminderService(HelperService):
    u"""
    The Kudubot Service that provides the anime reminder functionality
    """

    def init(self):
        u"""
        In addition to the normal initialization of a Service,
        this service initializes
        its database and starts the background thread
        """
        self.initialize_database_table(initializer=initialize_database)
        self.start_daemon_thread(self.background_loop)

    @staticmethod
    def define_requirements():
        u"""
        :return: The dependencies for this service
        """
        return []

    @staticmethod
    def define_identifier():
        u"""
        :return: The service's identifier
        """
        return u"anime_reminder"

    def handle_message(self, message):
        u"""
        Handles a message from the user

        :param message: The message to handle
        :return: None
        """
        mode = message.message_body.split(u" ")[1].lower()
        user = message.get_direct_response_contact()
        user_id = user.database_id

        params = message.message_body.split(u"\"")
        show = u"" if len(params) < 2 else params[1]

        if mode in [self.translate(u"@subscribe_command", x)
                    for x in self.supported_languages()]:

            result = u"@successful_add_message" \
                if store_subscription(user_id, show, self.connection.db) \
                else u"@exists_message"
            self.reply_translated(u"@reply_title", u"@subscribe_message_start " +
                                  show + u" " + result + u".", message)

        elif mode in [self.translate(u"@unsubscribe_command", x)
                      for x in self.supported_languages()]:

            result = u"@successful_remove_message" \
                if delete_subscription(user_id, show, self.connection.db) \
                else u"@does_not_exist_message"
            self.reply_translated(u"@reply_title",
                                  u"@unsubscribe_message_start " + show +
                                  u" " + result + u".", message)

        elif mode in [self.translate(u"@list_command", x)
                      for x in self.supported_languages()]:

            message_text = u"@subscription_list_message:\n\n"
            for subscription in get_subscriptions(self.connection.db, user_id):
                message_text += subscription[u"show_name"] + u"\n"
            self.reply_translated(u"@reply_title", message_text, message)

    def is_applicable_to(self, message):
        u"""
        Checks if a message is applicable to this Service

        :param message: The message to check
        :return: None
        """
        applicable = False
        for language in self.supported_languages():

            regex = u"^@command_name " \
                    u"(@list_command|@sub_unsub_command \"[^\"]+\")$"
            regex = re.compile(self.translate(regex, language))
            applicable = bool(re.search(regex, message.message_body)) \
                or applicable

        return applicable

    def define_syntax_description(self, language):
        u"""
        Defines the syntax description for the Service

        :param language: The language in which to display the syntax
                         description
        :return: The syntax description in the specified language
        """
        skeleton = u"@command_name @list_command\n"
        skeleton += u"@command_name @subscribe_command " \
                    u"\"@show_name_parameter\"\n"
        skeleton += u"@command_name @unsubscribe_command " \
                    u"\"@show_name_parameter\""
        return self.translate(skeleton, language)

    def define_language_text(self):
        u"""
        Defines the Language strings for the service for the implemented
        languages

        :return: The dictionary used to translate strings
        """
        return {
            u"@list_command": {u"en": u"list",
                              u"de": u"auflisten"},
            u"@subscribe_command": {u"en": u"subscribe",
                                   u"de": u"abonnieren"},
            u"@unsubscribe_command": {u"en": u"unsubscribe",
                                     u"de": u"abbestellen"},
            u"@sub_unsub_command": {u"en": u"(un)?subscribe",
                                   u"de": u"(abonnieren|abbestellen)"},
            u"@show_name_parameter": {u"en": u"Show Name",
                                     u"de": u"Serienname"},
            u"@command_name": {u"en": u"/anime-remind",
                              u"de": u"/anime-erinner"},
            u"@exists_message": {u"en": u"already exists",
                                u"de": u"existiert bereits"},
            u'@does_not_exist_message': {u"en": u"does not exist",
                                        u"de": u"existiert nicht"},
            u'@successful_add_message': {u"en": u"successful",
                                        u"de": u"wurde erfolgreich abonniert"},
            u'@successful_remove_message': {u"en": u"successfully removed",
                                           u"de": u"wurde erfolgreich "
                                                 u"abbestellt"},
            u"@subscribe_message_start": {u"en": u"Subscription for",
                                         u"de": u"Abonnement für"},
            u"@unsubscribe_message_start": {u"en": u"Subscription for",
                                           u"de": u"Abonnement für"},
            u"@reply_title": {u"en": u"Anime Reminder",
                             u"de": u"Anime Erinnerung"},
            u"@remind_title": {u"en": u"Anime Reminder",
                              u"de": u"Anime Erinnerung"},
            u"@subscription_list_message": {u"en": u"You are subscribed to the"
                                                 u"following shows",
                                           u"de": u"Du hast folgende Serien"
                                                 u"abonniert"},
            u"@episode": {u"en": u"episode",
                         u"de": u"Episode"},
            u"@has_been_released": {u"en": u"has been released! Discuss it"
                                         u"on reddit",
                                   u"de": u"wurde veröffentlicht! Diskuttier"
                                         u"sie auf reddit"},
            u"@help_message": {
                u"en": u"The Anime Reminder Service periodically checks for new "
                      u"anime discussion threads on reddit's "
                      u"r/anime board. A user can subscribe to specific shows "
                      u"and will then be notified whenever a "
                      u"new thread appears, which usually coincides with the "
                      u"point in time that the episode is "
                      u"available on streaming services like Crunchyroll, "
                      u"Amazon or Funimation.\n"
                      u"Users can also unsubscribe from shows and list all "
                      u"their subscriptions. Subscription names "
                      u"are case-insensitive.",
                u"de": u"Der Anime Erinnerungs-Service schaut in periodischen "
                      u"Abständen nach, ob neue Anime Diskussionen "
                      u"auf reddit.com/r/anime entstanden sind, welche neue "
                      u"Anime Episode diskuttieren. Ein Nutzer kann "
                      u"einzelne Serien abonnieren und wieder abbestellen. "
                      u"Für abonnierte Serien erhält der Nutzer "
                      u"eine Nachricht sobal eine neue Episode verfügbar ist."
                      u"Die Namen für die Abonnements achten nicht auf Groß- "
                      u"und Kleinschreibung. Man kann auch alle"
                      u"Abonnements die derzeit aktiv sind auflisten lassen."
            }
        }

    def define_help_message(self, language):
        u"""
        Defines the help message for the service

        :param language: The target language to translate the message to
        :return: The help message in the specified language
        """
        return self.translate(u"@help_message", language)

    def determine_language(self, message):
        u"""
        Determines the language used based on the incoming message

        :param message: The message to analyze
        :return: The language key to use
        """
        if message.message_body.startswith(self.define_command_name(u"de")):
            return u"de"
        else:
            return u"en"

    def define_command_name(self, language):
        u"""
        Defines the command name for the anime-remind functionality

        :param language: The language for which the command is valid
        :return: The command name in the specified language
        """
        return self.translate(u"@command_name", language)

    def background_loop(self):
        u"""
        Starts a new thread which will continuously check for new anime
        discussion threads on reddit.com/r/anime
        and notify users if they are subscribed to those shows

        :return: None
        """
        db = self.connection.get_database_connection_copy()
        while True:

            try:
                new_threads = scrape_reddit_discussion_threads()
            except requests.exceptions.ConnectionError:
                self.logger.error(u"Failed to connect")
                time.sleep(60)
                continue

            self.logger.debug(u"Checking for due subscriptions")

            for thread in new_threads:

                if not thread_exists(thread, db):
                    store_thread(thread, db)

                    for subscription in get_subscriptions(db):
                        if subscription[u"show_name"].lower() \
                                == thread[u"show_name"].lower():

                            receiver = self.connection.address_book\
                                .get_contact_for_id(
                                    subscription[u"user_id"], db
                                )

                            message_text = thread[u"show_name"] + u" @episode "
                            message_text += unicode(thread[u"episode"])
                            message_text += u" @has_been_released: "
                            message_text += thread[u"url"]

                            language = self.connection.language_selector.\
                                get_language_preference(
                                    receiver.database_id, db=db
                                )

                            message_text = \
                                self.translate(message_text, language)
                            title = self.translate(u"@remind_title", language)

                            self.connection.send_message(Message(
                                title, message_text, receiver,
                                self.connection.user_contact)
                            )

            time.sleep(60)
