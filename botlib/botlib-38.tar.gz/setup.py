#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BOTLIB Framework to program bots
#
# setup.py
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

""" botlib setup.py """

import os
import sys

if sys.version_info.major < 3:
    print("you need to run BOTLIB with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

setup(
    name='botlib',
    version='38',
    url='https://bitbucket.org/bthate/botlib',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Framework to program bots",
    license='MIT',
    include_package_data=False,
    zip_safe=False,
    install_requires=["sleekxmpp==1.3.1", "feedparser>=5.2.1", "dnspython", "pyasn1_modules","pyasn1>=0.3.2", "requests"],
    scripts=["bot", "bin/bot-do", "bin/bot-docs", "bin/bot-local", "bin/bot-udp"],
    packages=['botlib'],
    extra_path="botlib",
    long_description='''BOTLIB is a python3 framework to use if you want to program CLI, IRC or XMPP bots.

features
========

BOTLIB provides the following features:

::

 object class	 	save/load to/from a json file.
 rest server 		serve saved object’s over http.
 rss fetcher 		echo rss feeds to irc channels.
 udp server 		udp to bot to irc channel.
 watcher server 	run tail -f and have output send to IRC channel.
 email scanning 	scan mbox format to searchable botlib objects.
 json backend 		objects are stored as json string in files on the fs.
 db			iteration over stored objects.
 timestamp		time based filenames gives logging capabilities
 future			future sensors should provide entry to the logger.

install
=======

Clone the source:

:: 

 bart@okdan:~$ hg clone https://bitbucket.org/bthate/botlib

 You might need to do one of the following if the bot doesn't work:

 bart@okdan:~/botlib$ export PYTHONPATH="."
 bart@okdan:~/botlib$ export PYTHONIOENCODING="utf-8"

Another option is to download with pip3 and install globally:

::

 bart@okdan:~$ pip3 install botlib --upgrade

irc
===

Use -n <nick>, -s <server>, -c <channel> options to make the bot join the network:

::

 bart@okdan:~$ bot -i irc -n botlib -s irc.freenode.net -c \#botlib

You can use the -w option to write config values to ~/.bot/config/irc

xmpp
====

For the xmpp server use a ~/.sleekpass file with the password in it:

::

 bart@okdan:~$ cat "password" > ~/.sleekpass
 bart@okdan:~$ bot -i xmpp,rss --room=test@conference.localhost

users
=====

One needs to add a users origin to be able to give the bot commands. One can add a user with the meet command:

::

 bart@okdan:~$ bot meet user@server
 user user@server created

To give the user a permission you can use the perm command:

::

 bart@okdan:~$ bot perm user@server ps
 ok user@server

The u command show the json dump of a user object:

::

 bart@okdan:~$ bot u user@server 
 {
     "_container": {
         "default": "",
         "path": "/home/bart/.bot/user/2017-10-12/21:05:52.095737",
         "prefix": "object",
         "saved": "Thu Oct 12 21:07:03 2017",
         "signature": "c113c4125f8c2a88d5b312e283792ae019c61a52"
     },
     "_type": "<class 'botlib.object.Object'>",
     "origin": "user@server",
     "perms": [
         "USER",
         "PS"
     ],
     "user": "user@server"
 }

The default shell user is root@shell and gives access to all the commands that are available.

commands
========

The following commands are available:

::

 alias                 key, value alias. 
 announce              announce text on all channels in fleet. 
 begin                 begin stopwatch. 
 cfg                   edit config files. 
 cmnds                 show list of commands. 
 deleted               show deleted records. 
 delperm               delete permissions of an user. 
 dump                  dump objects matching the given criteria. 
 edit                  edit and save objects. 
 end                   stop stopwatch. 
 exit                  stop the bot. 
 fetcher               fetch all rss feeds. 
 find                  present a list of objects based on prompt input. 
 first                 show the first record matching the given criteria. 
 fix                   fix a object by loading and saving it. 
 idle                  see how long a channel/nick has been idle. 
 last                  show last objectect matching the criteria. 
 license               display BOTLIB license. 
 load                  force a plugin reload. 
 log                   log some text. 
 loglevel              set loglevel. 
 loud                  disable silent mode of a bot. 
 ls                    show subdirs in working directory. 
 man                   show descriptions of the available commands. 
 mbox                  convert emails to botlib objects. 
 meet                  create an user record. 
 nick                  change bot nick on IRC. 
 perm                  add/change permissions of an user. 
 permissions           show permissions granted to a user. 
 perms                 show permission of user. 
 pid                   show pid of the BOTLIB bot. 
 ps                    show running threads. 
 reboot                reboot the bot, allowing statefull reboot (keeping connections alive). 
 reload                reload a plugin. 
 restore               set deleted=False in selected records. 
 rm                    set deleted flag on objects. 
 rss                   add a rss url. 
 save                  make a kernel dump. 
 shop                  add a shopitem to the shopping list. 
 show                  show dumps of basic objects. 
 silent                put a bot into silent mode. 
 start                 start a plugin. 
 stop                  stop a plugin. 
 synchronize           synchronize rss feeds (fetch but don't show). 
 test                  echo origin. 
 timer                 timer command to schedule a text to be printed on a given time. stopwatch to measure elapsed time. 
 today                 show last week's logged objects. 
 todo                  log a todo item. 
 tomorrow              show todo items for tomorrow. 
 u                     show user selected by userhost. 
 uptime                show uptime. 
 version               show version. 
 w                     show user data. 
 watch                 add a file to watch (monitor and relay to channel). 
 week                  show last week's logged objects. 
 whoami                show origin. 
 yesterday             show last week's logged objects. 

modules
=======

The following modules are available:

::

 botlib.bot		bot base class.
 botlib.cli		command line interfacce bot, gives a shell prompt to issue bot commands.
 botlib.clock		timer, repeater and other clock based classes.
 botlib.cmnds		botlib basic commands.
 botlib.compose		construct a object into it’s type.
 botlib.decorator	method decorators
 botlib.db		JSON file db.
 botlib.engine		select.epoll event loop, easily interrup_table esp. versus a blocking event loop.
 botlib.error		botlib exceptions.
 botlib.event		event handling classes.
 botlib.fleet		fleet is a list of bots.
 botlib.handler		schedule events.
 botlib.irc		IRC bot class.
 botlib.kernel		program boot and module loading.
 botlib.launcher	a launcher launches threads (or tasks in this case).
 botlib.log		log module to set standard format of logging.
 botlib.object		JSON file backed object with dotted access.
 botlib.raw		raw output using print.
 botlib.rss		rss module.
 botlib.selector	functions used in code to select what objects to use.
 botlib.task		adapted thread to add extra functionality to threads.
 botlib.trace		functions concering stack trace.
 botlib.users		class to access user records.
 botlib.xmpp		XMPP bot class.
 botlib.register	object with list for multiple values.
 botlib.rest		rest interface.
 botlib.runner		threaded loop to run tasks on.
 botlib.space		central module to store objects in.
 botlib.static		static definitions.
 botlib.template	cfg objects containing default values for various services and plugins.
 botlib.test		plugin containing test commands and classes.
 botlib.udp		relay txt through a udp port listener.
 botlib.utils		lib local helper functions.
 botlib.url		functions that fetch data from url.
 botlib.watcher		watch files.
 botlib.worker		worker thread that handles submitted jobs through Worker.put(func, args, kwargs).
 botlib.wisdom  	wijsheid, wijs !

programming
===========

BOTLIB makes it possible to program your own module enabling your own commands.

code example:

::

     def hi(event):
         event.reply("hi %s" % event.origin)


user programmed modules are read from a botmods directory in your current
working directory, you can put your .py files over there.

license
=======

BOTLIB has a MIT license.

::

 # -*- coding: utf-8 -*-
 #
 # BOTLIB Framework to program bots
 #
 # LICENSE
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
 # The above copyright notice and this permission notice don't have to be included.in 
 # .
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

contact
=======

| Bart Thate
| botfather on #dunkbot irc.freenode.net
| bthate@dds.nl, thatebart@gmail.com
| hg clone ssh://bart_thate@hg.osdn.net//hgroot/botlib/botlib


''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
