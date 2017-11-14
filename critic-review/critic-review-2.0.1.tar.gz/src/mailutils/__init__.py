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

import json
import os
import time

from email.utils import parseaddr

import dbutils

def getSystemEmail():
    import api
    import base

    system_email = api.critic.settings().system.email
    if system_email is None:
        system_username = base.configuration()["system.username"]
        system_hostname = api.critic.settings().system.hostname
        system_email = f"{system_username}@{system_hostname}"
    return system_email

def generateMessageId(index=1):
    now = time.time()

    timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime(now))
    timestamp_ms = "%04d" % ((now * 10000) % 10000)

    return "%s.%s.%04d" % (timestamp, timestamp_ms, index)

class User():
    def __init__(self, name, fullname, email):
        self.name = name
        self.fullname = fullname
        self.email = email

def queueMail(from_user, to_user, recipients, subject, body,
              message_id=None, parent_message_id=None, headers=None):
    import api

    if not message_id:
        message_id = generateMessageId()

    if headers is None:
        headers = {}
    else:
        headers = headers.copy()

    if parent_message_id:
        parent_message_id = "<%s@%s>" % (parent_message_id,
                                         api.critic.settings().system.hostname)

    filename = ("%s/%s_%s_%s.txt.pending"
                % (os.path.join(api.critic.settings().paths.home, "outbox"),
                   from_user.name, to_user.name, message_id))

    def user_json(value):
        if isinstance(value, (User, dbutils.User)):
            return {"fullname": value.fullname, "email": value.email}
        fullname, email = parseaddr(value)
        return {"fullname": fullname, "email": email}

    with open(filename, "w", encoding="utf-8") as file:
        json.dump({
            "message_id": message_id,
            "parent_message_id": parent_message_id,
            "headers": headers,
            "time": time.time(),
            "from_user": user_json(from_user),
            "to_user": user_json(to_user),
            "recipients": [user_json(recipient) for recipient in recipients],
            "subject": subject,
            "body": body
        }, file)

    return filename

def sendMessage(recipients, subject, body):
    import api
    import base

    from_user = User(base.configuration()["system.username"], "Critic System",
                     getSystemEmail())
    filenames = []

    for to_user in recipients:
        if isinstance(to_user, str):
            fullname, email = parseaddr(to_user)
            name, _, _ = email.partition("@")
            name, _, _ = email.partition("+")
            to_user = User(name, fullname, email)

        filenames.append(queueMail(
            from_user, to_user, recipients, subject, body))

    sendPendingMails(filenames)

def sendAdministratorMessage(source, summary, message):
    import api

    recipients = []

    for recipient in api.critic.settings().system.recipients:
        recipients.append(recipient)

    sendMessage(recipients, "%s: %s" % (source, summary), message)

def sendAdministratorErrorReport(db, source, summary, message):
    if db:
        installed_sha1 = dbutils.getInstalledSHA1(db)
    else:
        installed_sha1 = "<unknown>"
    sendAdministratorMessage(source, summary, """\

Critic encountered an unexpected error.  If you know a series of steps that can
reproduce this error it would be very useful if you submitted a bug report
including the steps plus the information below (see bug reporting URL at the
bottom of this e-mail).

%(message)s

Critic version: %(installed_sha1)s
Critic bug reports can be filed here: https://github.com/jensl/critic/issues/new
""" % { "message": message, "installed_sha1": installed_sha1 })

def sendExceptionMessage(db, source, exception):
    lines = exception.splitlines()
    sendAdministratorErrorReport(db, source, lines[-1], exception.rstrip())

def sendPendingMails(filenames):
    import background.utils

    wakeup_service = False

    for filename in filenames:
        assert filename.endswith(".txt.pending")
        try:
            os.rename(filename, filename[:-len(".pending")])
            wakeup_service = True
        except OSError:
            pass

    if wakeup_service:
        background.utils.wakeup("maildelivery")

def cancelPendingMails(filenames):
    for filename in filenames:
        assert filename.endswith(".txt.pending")
        try:
            os.unlink(filename)
        except OSError:
            pass
