#!/usr/bin/python
# -*- coding: utf-8 -*-

# alarm.py

# Copyright 2014-2017 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# CLI Alarm Clock

# https://github.com/dslackw/alarm

# Alarm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import datetime
import calendar


__all__ = "alarm"
__author__ = "dslackw"
__version_info__ = (2, 2)
__version__ = "{0}.{1}".format(*__version_info__)
__license__ = "GNU General Public License v3 (GPLv3)"
__email__ = "d.zlatanidis@gmail.com"

# check if Mplayer installed
_found_mplayer = None
for dr in os.environ["PATH"].split(os.pathsep):
    if os.path.exists(os.path.join(dr, "mplayer")):
        _found_mplayer = dr
if not _found_mplayer:
    print("Error: Mplayer required !")
    sys.exit()

configuration = [
    "# configuration file for alarm\n\n",
    "[Day]\n",
    "# Choose 'today' if you do not want to regulate daily day.\n",
    "DAY=today\n\n",
    "[Alarm Time]\n",
    "# Constant alarm time.\n",
    "ALARM_TIME=HH:MM\n\n",
    "[Alarm Attempts]\n",
    "# Select number for attempts.\n",
    "ATTEMPTS=5\n\n",
    "[Path]\n",
    "# Path statements sound files.\n",
    "SONG=/path/to/song.mp3"
]

HOME = os.getenv("HOME") + "/"
alarm_config_dir = ".alarm"
config_file = "config"
alarm_config = ("%s%s/%s" % (HOME, alarm_config_dir, config_file))
if not os.path.exists(HOME + alarm_config_dir):
    os.mkdir(HOME + alarm_config_dir)
if not os.path.isfile(alarm_config):
    with open(alarm_config, "w") as conf:
        for line in configuration:
            conf.write(line)
        conf.close()


def config():
    """
        Reading config file in $HOME directory
        /home/user/.alarm/config
    """
    alarm_day = alarm_time = alarm_attempts = song = []
    for line in open(alarm_config, "r"):
        line = line.lstrip()
        if line.startswith("DAY"):
            alarm_day = line[4:].split()
        if line.startswith("ALARM_TIME"):
            alarm_time = line[11:].split()
        if line.startswith("ATTEMPTS"):
            alarm_attempts = line[9:].split()
        if line.startswith("SONG"):
            song = line[5:].split()
    if alarm_day == ["today"]:
        alarm_day = time.strftime("%d").split()
    alarm_args = alarm_day + alarm_time + alarm_attempts + song
    if alarm_args:
        if len(alarm_args) == 4:
            return alarm_args
        else:
            print("Error: config file: missing argument")
            sys.exit()
    else:
        print("Error: config file: missing argument")
        sys.exit()


class MplayerNotInstalledException(Exception):
    def __init__(self):
        print("Error: Mplayer required for playing alarm sounds\n")


class ALARM(object):
    """
        CLI Alarm Clock
    """
    def __init__(self, alarm_day, alarm_time, alarm_attempts, song):

        self.wakeup = ["__        __    _          _   _         _ ",
                       "\ \      / /_ _| | _____  | | | |_ __   | |",
                       " \ \ /\ / / _` | |/ / _ \ | | | | '_ \  | |",
                       "  \ V  V / (_| |   <  __/ | |_| | |_) | |_|",
                       "   \_/\_/ \__,_|_|\_\___|  \___/| .__/  (_)",
                       "                                |_|\n"]
        self.RUN_ALARM = True
        self.alarm_day = alarm_day
        self.alarm_time = alarm_time.replace(":", " ").split()  # split items
        self.alarm_pattern = ["HH", "MM"]
        self.alarm_attempts = alarm_attempts
        self.song = song
        self.mplayer_options = "-really-quiet"
        try:
            self.alarm_hour = self.alarm_time[0]
            self.alarm_minutes = self.alarm_time[1]
        except IndexError:      # if one value in list
            print("error: time: usage 'HH:MM'")
            self.alarm_hour = "00"
            self.alarm_minutes = "00"
            self.alarm_time = [self.alarm_hour, self.alarm_minutes]
            self.RUN_ALARM = False

    def errors(self):
        """
        Check for usage errors
        """
        try:
            self.now = datetime.datetime.now()
            if len(self.alarm_day) < 2 or len(self.alarm_day) > 2:
                print("error: day: usage 'DD' such us '0%s' not '%s'" % (
                    self.alarm_day, self.alarm_day))
                self.RUN_ALARM = False
            if int(self.alarm_day) > calendar.monthrange(
                    self.now.year, self.now.month)[1] or int(
                        self.alarm_day) < 1:
                print("error: day: out of range")
                self.RUN_ALARM = False
            # compare alarm time with alarm pattern
            if (len(self.alarm_time) != len(self.alarm_pattern) or
                    len(self.alarm_time[0]) < 2 or
                    len(self.alarm_time[0]) > 2 or
                    len(self.alarm_time[1]) < 2 or len(self.alarm_time[1]) > 2):
                print("error: time: usage '%s'" % ":".join(self.alarm_pattern))
                self.RUN_ALARM = False
            # compare if alarm hour or alarm minutes
            # is within the range
            if int(self.alarm_hour) not in range(0, 24):
                print("error: hour: out of range")
                self.RUN_ALARM = False
            if int(self.alarm_minutes) not in range(0, 60):
                print("error: minutes: out of range")
                self.RUN_ALARM = False
        except ValueError:
            print("Usage '%s'" % ":".join(self.alarm_pattern))
            self.RUN_ALARM = False
        if not os.path.isfile(self.song):
            print("error: song: file does not exist")
            self.RUN_ALARM = False

    def start(self):
        """
        All the work going on here. To the Authority the right day and time
        format and finding the correct path of the file. The Application
        requires Mplayer to play the alarm sound. Please read which sounds
        are supported in page:
        http://web.njit.edu/all_topics/Prog_Lang_Docs/html/mplayer/formats.html
        """
        self.errors()
        try:
            alarm_day_name = calendar.day_name[calendar.weekday(
                self.now.year, self.now.month, int(self.alarm_day))]
        except ValueError:
            pass
        self.alarm_time.insert(0, self.alarm_day)
        self.alarm_time = ":".join(self.alarm_time)     # reset begin format
        if self.RUN_ALARM:
            os.system("clear")
            print("+" + "=" * 78 + "+")
            print("|" + " " * 30 + "CLI Alarm Clock" + " " * 33 + "|")
            print("+" + "=" * 78 + "+")
            print("| Alarm set at : %s %s" % (
                  alarm_day_name, self.alarm_time[3:]) + " " * (
                  62-len(alarm_day_name + self.alarm_time[2:])) + "|")
            print("| Sound file : %s" % self.song + " " * (64-len(
                self.song)) + "|")
            print("| Time : " + " " * 70 + "|")
            print("+" + "=" * 78 + "+")
            print("Press 'Ctrl + c' to cancel alarm ...")
            try:
                while self.RUN_ALARM:
                    start_time = time.strftime("%d:%H:%M:%S")
                    self.position(6, 10, self.color(
                        "green") + start_time[3:] + self.color("endc"))
                    time.sleep(1)
                    begin = start_time[:-3]
                    # if start_time[0] == '0':
                    #    begin = start_time[1:-3]
                    if begin == self.alarm_time:
                        self.position(6, 10, self.color(
                            "red") + start_time[3:-3] + self.color(
                                "endc") + " Wake Up !")
                        for wake in self.wakeup:
                            print(wake)
                        print("\nPress 'SPACE' to pause alarm ...\n")
                        if not self.alarm_attempts:
                            self.alarm_attempts = 5
                        else:
                            self.alarm_attempts = int(self.alarm_attempts)
                        for att in range(0, self.alarm_attempts):
                            print("Attempt %d\n" % (att + 1))
                            play = os.system("mplayer %s '%s'" % (
                                self.mplayer_options, self.song))
                            # catch if mplayer not installed
                            # if play return 0 all good
                            # 256=KeyboardInterupt
                            if play != 0 and play != 256:
                                MplayerNotInstalledException()
                                break
                        self.RUN_ALARM = False
            except KeyboardInterrupt:
                print("\nAlarm canceled!")
                self.RUN_ALARM = False

    def position(self, x, y, text):
        """
            ANSI Escape sequences
            http://ascii-table.com/ansi-escape-sequences.php
        """
        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
        sys.stdout.flush()

    def color(self, color):
        """
            Print foreground colors
        """
        paint = {
            "red": "\x1b[31m",
            "green": "\x1b[32m",
            "endc": "\x1b[0m"
        }
        return paint[color]


class Args(object):

    def __init__(self):
        pass

    def view(self):
        """Usage: alarm [OPTIONS] <day> <alarm_time> <song>

Optional arguments
  -h, --help       show this help message and exit
  -v, --version    print version and exit
  -s, --set        set alarm day, time and sound

  --config         use config file

  Example: alarm -s 21 06:00 /path/to/song.mp3
  """
        print(self.view.__doc__)


def main():
    args = sys.argv
    args.pop(0)
    if len(args) == 0:
        print("try alarm --help")
    elif len(args) == 1 and args[0] == "-h" or args[0] == "--help":
        Args().view()
    elif len(args) == 1 and args[0] == "-v" or args[0] == "--version":
        print("Version : %s" % __version__)
    elif (len(args) == 4 and args[0] == "-s" or len(args) == 4 and
          args[0] == "--set"):
        ALARM(alarm_day=args[1], alarm_time=args[2], alarm_attempts="",
              song=args[3]).start()
    elif len(args) == 1 and args[0] == "--config":
        alarm_set_args = config()
        ALARM(alarm_set_args[0], alarm_set_args[1], alarm_set_args[2],
              alarm_set_args[3]).start()
    else:
        print("try alarm --help")

if __name__ == "__main__":
    main()
