# BOTLIB Framework to program bots
#
# botlib/fleet.py
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

""" fleet is a list of bots. """

from botlib.bot import Bot
from botlib.object import Object

class Fleet(Object):

    """ Fleet is a list of bots. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bots = []

    def __iter__(self):
        for bot in self.bots:
            yield bot

    def add(self, bot):
        """ insert a bot into a fleet. """
        if type(bot) == dict:
            bot = Bot(bot)
        self.bots.append(bot)

    def echo(self, id, txt):
        """ echo txt to a specific bot. """
        for bot in self.bots:
            if bot.id() == id:
                bot.raw(txt)

    def get_bots(self, id):
        """ return bots with botid in the fleet. """
        for bot in self.bots:
            if id in bot.id():
                yield bot

    def get_bot(self, id):
        """ return bot with botid in the fleet. """
        for bot in self.bots:
            if id in bot.id():
                return bot

    def get_origin(self, nick):
        """ query bot in the fleet for a nick/origin match. Returns the origin. """
        for bot in self.bots:
            try:
                return bot._userhosts[nick]
            except (KeyError, AttributeError):
                pass
        return nick

    def get_type(self, btype):
        """ return bot with botid in the fleet. """
        for bot in self.bots:
            if btype in bot._type:
                yield bot

    def partyline(self, txt):
        """ NEEDS IMPLEMENTING. """
        pass

    def remove(self, bot):
        """ remove a bot from fleet. """
        if bot in self.bots:
            self.bots.remove(bot)

    def say_id(self, id, channel, txt, type):
        """ echo text to channel on bot matching the given id. """
        bots = self.get_bots(id)
        for bot in bots:
            bot.say(channel, txt, type)
