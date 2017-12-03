# BOTLIB Framework to program bots
#
# botlib/email.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" botlib basic commands. """

from botlib.trace import get_exception
from botlib.object import Object
from botlib.utils import to_date

import logging
import mailbox
import os
import re
import tempfile

class Email(Object):
    """ email object. """
    pass

def mbox(event):
    """ convert emails to botlib objects. """
    if not event._parsed.rest:
        event.reply("mbox <path>")
        return
    fn = os.path.expanduser(event._parsed.args[0])
    event.reply("reading from %s" % fn)
    nr = 0
    if os.path.isdir(fn):
        thing = mailbox.Maildir(fn, create=False)
    elif os.path.isfile(fn):
        thing = mailbox.mbox(fn, create=False)
    else:
        event.reply("need a mbox or maildir.")
        return
    try:
        thing.lock()
    except FileNotFoundError:
        pass
    for m in thing:
        try:
            o = Email()
            o.update(m.items())
            try:
                sdate = os.sep.join(to_date(o.Date).split())
            except AttributeError:
                sdate = None
            o.text = ""
            for payload in m.walk():
                if payload.get_content_type() == 'text/plain':
                    o.text += payload.get_payload()
            o.text = o.text.replace("\\n", "\n")
            if sdate:
                o.save(stime=sdate)
            else:
                o.save()
            nr += 1
        except:
            logging.error(get_exception())
    if nr:
        event.ok(nr)

mbox._threaded = True
mbox.perm = "MBOX"

def output(text):
    frm = ""
    subject = ""
    for i in text:
        try:
            b = fromre.search(i)
            if b:
                 frm = b.group(0).strip()
            c = subjectre.search(i)
            if c:
                subject = c.group(0).strip()
            if frm and subject:
                break
        except Exception:
            pass
    if frm and subject:
        result = "%s %s" % (frm, subject)
        out(result)

def save_email(text):
    fp = tempfile.NamedTemporaryFile()
    thing = mailbox.mbox(fp.name, create=False)
    thing.add(text)
    try:
        thing.lock()
    except FileNotFoundError:
        pass
    for m in thing:
        try:
            o = Email()
            o.update(m.items())
            try:
                sdate = os.sep.join(to_date(o.Date).split())
            except AttributeError:
                sdate = None
            o.text = ""
            for payload in m.walk():
                if payload.get_content_type() == 'text/plain':
                    o.text += payload.get_payload()
            o.text = o.text.replace("\\n", "\n")
            if sdate:
                o.save(stime=sdate)
            else:
                o.save()
        except:
            logging.error(get_exception())

