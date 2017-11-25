#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#Copyright (c) 2017, George Tokmaji

#Permission to use, copy, modify, and/or distribute this software for any
#purpose with or without fee is hereby granted, provided that the above
#copyright notice and this permission notice appear in all copies.
#
#THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
sys = os.sys

import socket
import subprocess
import queue
import threading
from time import sleep
from platform import architecture

import re
import configparser
from io import BytesIO
import urllib.request
import random
import traceback

import tarfile
from enum import IntEnum

from gzip import GzipFile

import asyncio
from blinker import signal
from asyncirc import irc
import asyncirc.plugins.addressed

#
# Helpers
#

class list(list):
    """ Extended list """
    
    def __lshift__(self, other):
        self.append(other)
        return self

    def __rshift__(self, other):
        if isinstance(other, list):
            item = self.__getitem__(len(self) - 1)
            try:
                other.append(item)
                self.pop()
            except Exception:
                raise TypeError("Cannot pass item to {}!".format(other)) from None
    
    # Methods
    
    def isEmpty(self):
        return len(self) == 0

class Updater(object):
    parent = None
    __current_revision = ""
    lookuptable = {"64bit" : "amd64", "32bit" : "i386"}
    
    def __init__(self, parent):
        self.parent = parent
        with open(os.path.join(self.parent.path, "snapshot.id"), "rb") as fobj:
            self.__current_revision = fobj.read().decode("utf-8")
        start_new_thread(self.checkForUpdates, ())
    
    @property
    def current_revision(self):
        return self.__current_revision
    
    @current_revision.setter
    def current_revision(self, other):
        self.__current_revision = other
        if type(other) == str:
            try:
                other = other.encode("utf-8")
            except Exception:
                raise TypeError("Wrong datatype!") from None
        
        with open(os.path.join(self.parent.path, "snapshot.id"), "wb") as fobj:
            fobj.write(other)
    
    def checkForUpdates(self):
        while True:
            try:
                site = urllib.request.urlopen(self.parent.config["Addresses"]["snapshotList"]).read().decode("utf-8").split(self.parent.config["Updater"]["SplitString"])
                site.remove(site[0])
                site = [i.split("' title")[0] for i in site]
                
                x = None
                for i in site:
                    x = re.match(self.parent.config["RegExps"]["Snapshot"].format(sys.platform, self.lookuptable[architecture()[0]]), i)
                    if x:
                        rev = x.group(2)
                        
                        if self.current_revision != rev:
                            self.current_revision = rev
                            self.loadNewSnapshot(x)
                        
                        break
                if not x:
                    print("Updater.checkForUpdates: Regular expression doesn't match!", file=sys.stderr)
            
            except Exception as e:
                traceback.print_exc()
            finally:
                sleep(10)
    
    def loadNewSnapshot(self, reg):
        print(f"Updater: Downloading snapshot with id {self.current_revision}")
        with open(os.path.join(self.parent.path, "snapshot"), "wb") as fobj:
            fobj.write(urllib.request.urlopen(self.parent.config["Addresses"]["snapshotDownload"].format(reg.group(0).split("' title")[0])).read())
        
        #extract the snapshot
        tar = tarfile.open(os.path.join(self.parent.path, "snapshot"), mode="r:bz2")
        tar.extractall(path=self.parent.path)
        print("Updater: New snapshot has been extracted.")
        
        #get the openclonk-server autobuild
        site = json.loads(urllib.request.urlopen(self.parent.config["Addresses"]["autobuildList"]).read().decode("utf-8"))
        
        for commit in site:
            for build in commit["builds"]:
                if re.match(r"{}-{}-.*".format(sys.platform, self.lookuptable[architecture()[0]]), build["platform"]["triplet"]):
                    for b in build["components"]:
                        reg = re.match(self.parent.config["RegExps"]["Autobuild"], str(b["path"])) #skip the engine check as the only useful one is openclonk-server
                        if reg and (reg.group(1), reg.group(2), reg.group(3)) == (self.current_revision[:-3], sys.platform, self.lookuptable[architecture()[0]]):
                            print(f"Updater: Downloading autobuild with id {self.current_revision}")
                            buffer = BytesIO()
                            buffer.write(urllib.request.urlopen(self.parent.config["Addresses"]["autobuildDownload"].format(b["path"])).read())
                            buffer.seek(0)
                            with open(os.path.join(self.parent.path, self.parent.config["Updater"]["BinaryName"]), "wb") as fobj:
                                fobj.write(GzipFile(fileobj=buffer).read())
                                
                            print("Updater: New openclonk-server build has been extracted.")
                            os.chmod(os.path.join(self.parent.path, self.parent.config["Updater"]["BinaryName"]), os.stat(os.path.join(self.parent.path, self.parent.config["Updater"]["BinaryName"])).st_mode | 64)
                            return True
        
        

class PyCRCtrl(object):
    """Server control"""
    irc = None
    
    clonk = None
    server_thread = None
    stopped = False
    config = configparser.ConfigParser()
    
    scenario = ""
    commands = {}
    
    path = None
    config_path = None
    scenlist = []
    league_scenlist = []
    
    topic = "Kein laufendes Spiel."
    
    __state = "Lobby"
    __ingamechat = "aktiviert"
    
    updater = None
    shutdowned = False
    
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, text):
        if text in ["Lobby", "Lädt", "Läuft"]:
            self.__state = text
            self.setTopic("Aktuelles Szenario: {} | {}{} | Ingamechat ist {}.".format(self.scenario, self.state, (" | Liga" if self.scenario in self.league_scenlist else ""), self.ingamechat))
    
    @property
    def ingamechat(self):
        return self.__ingamechat
    
    @ingamechat.setter
    def ingamechat(self, text):
        if text in ["aktiviert", "deaktiviert"]:
            self.__ingamechat = text
            self.state = self.state
    
    def __init__(self, path, config="pycrctrl.ini"):
        self.path = path
        self.loadConfigFile(config)
        self.ingamechat = "aktiviert" if self.config["IRC"].getboolean("Ingamechat") else "deaktiviert"
        self.loadScenarioList()
        self.startIRC()
        
        self.queue = queue.Queue(5)
        if self.config["Updater"].getboolean("Enabled"):
            self.updater = Updater(self)
    
    def loadScenarioList(self) -> None:
        if self.path == None:
            raise OSError("No path specified")
        
        with open(os.path.join(self.path,"scenarios.lst"), "r") as fobj:
            self.scenlist = fobj.readlines()
        
        with open(os.path.join(self.path, "scenarios_league.lst"), "r") as fobj:
            self.league_scenlist = fobj.readlines()
        
        print("DEBUG: Scenario lists loaded.")
    
    def startIRC(self) -> None:
        asyncirc.plugins.addressed.register_command_character(self.config["General"]["Prefix"])
        self.irc = irc.connect(self.config["IRC"]["Server"], self.config["IRC"]["Port"], use_ssl=self.config["IRC"].getboolean("SSL"))
        self.irc.register(*([self.config["IRC"]["Nick"]] * 3), password=self.config["IRC"]["Password"])
        self.irc.join([*(list(self.config["Channels"].values())), "#openclonk-atlantis"])
        
    def loadConfigFile(self, config) -> None:
        if self.path == None:
            raise OSError("No path specified")
        
        parser = configparser.ConfigParser()
        self.config_path = conf = os.path.join(self.path, config)
        
        if os.path.isdir(conf):
            raise OSError("{} is a directory!".format(conf))
        
        elif os.path.isfile(conf):
            self.config.read(conf)
        
        elif not os.path.exists(conf):
            c = """[General]
Prefix=@

[Clonk]
Engine=clonk
Encoding=utf-8
Commandline=/fullscreen /lobby:300 /record /faircrew
Autohost=false

[IRC]
Ingamechat=false
Nick=PyCRCtrl
Password=
Server=irc.euirc.net
Port=6667
SSL=false

[Channels]
Parent=
Ingame=

[Updater]
Enabled=false
BinaryName=
SplitString=

[Addresses]
snapshotList=http://openclonk.org/nightly-builds
snapshotDownload=http://openclonk.org/builds/nightly/snapshots/{}
autobuildList=https://autobuild.openclonk.org/api/v1/jobs
autobuildAddress=https://autobuild.openclonk.org/static/binaries/{}

[RegExps]
LobbyStart=((?:Los geht's!|Action go!)\\s*)
Start=Start!
PlayerJoin=^Client (.+) (?:verbunden|connected)\.\s*$
PlayerLeave=^Client (.+) (?:entfernt|removed).*
Shutdown=Spiel ausgewertet.*
Autobuild=.*/openclonk-server-(.*)-(.*)-(.*)-.*
Snapshot=openclonk-snapshot-(.*)-(.*)-{}-{}-."""
            
            self.config.read_string(c)
            with open(conf, "w") as fobj:
                self.config.write(fobj)
    
    def startClonk(self):
        try:
            while True:
                if self.scenario == "":
                    if self.queue.empty() == False:
                        self.scenario = self.queue.get()
                    else:
                        self.scenario = random.choice(self.scenlist).splitlines()[0]
                
                self.clonk = subprocess.Popen(
                    './{} {} "{}"'.format(self.config["Clonk"]["Engine"], self.config["Clonk"]["Commandline"] + " " + self.config["Clonk"]["commandlinePrefix"]  + ("league" if self.scenario in self.league_scenlist else "noleague"), self.scenario),
                    0,
                    None,
                    subprocess.PIPE,
                    subprocess.PIPE,
                    subprocess.STDOUT,
                    shell=True,
                    cwd=self.path,
                    encoding=self.config["Clonk"]["Encoding"]
                    )
                self.state = "Lobby"
                self.readServerOutput()
                if self.config["Clonk"].getboolean("Autohost") == False:
                    self.server_thread = None
                    self.setTopic("Kein laufendes Spiel.") 
                    break
        
        finally:
            if self.clonk:
                self.clonk.stdin.close()
    
    def readServerOutput(self):
        while True:
            try:
                output = self.clonk.stdout.readline()
                
                if re.match(self.config["RegExps"]["Shutdown"], output):
                    self.clonk.stdin.close()
                elif output == "" and self.clonk.poll() is not None:
                    if self.clonk:
                        self.clonk.stdin.close()
                        self.clonk = None
                        self.scenario = ""
                        return
                
                elif output:
                    output = output.strip()
                    output = output[(output.find("] ") if output.find("] ") != -1 else -2) + len("] "):] # TODO: Make this code readable
                    
                    if output[0] == ">":
                        output = output[1:]
                    
                    print(output)
                    
                    self.checkForCommands(output, reply=self.writeToServer)
                    
                    if re.match(self.config["RegExps"]["LobbyStart"], output):
                        self.state = "Lädt"
                
                    elif re.match(self.config["RegExps"]["Start"], output):
                        self.state = "Läuft"
                
                    if self.ingamechat == "aktiviert":
                        if self.isMessage(output) and f"<{self.irc.nickname}>" not in output:
                                self.irc.say(self.config["Channels"]["Ingame"], f"[Clonk]{output}")
                        
                        elif (re.match(self.config["RegExps"]["PlayerJoin"], output) or re.match(self.config["RegExps"]["PlayerLeave"], output)):
                            self.irc.say(self.config["Channels"]["Ingame"], output)
                
                
            except KeyboardInterrupt:
                if self.clonk.stdin:
                    self.clonk.stdin.close()
            
            except Exception as e:
                traceback.print_exc()
                continue
    
    def checkForCommands(self, msg, reply) -> None:
        part = self.isCommand(msg)
        if part and part[1] != self.irc.nick:
            cmd = part[2].split(" ", 1)
            found = False
            if len(cmd) > 0:
                key = cmd[0].strip()
                
                if signal(f"cmd-{key}").receivers:
                    found = True
                
                msg = [reply]
                msg.extend(cmd[1].strip().split(" ") if len(cmd) > 1 else [])
                
                signal(f"cmd-{key}").send(msg)
            
            if not found:
                reply('Unbekannter Befehl: "' + part[2] + '"!')
    
    def isMessage(self, msg):
        if self.isCommand(msg):
            return
        
        return re.match(self.config["RegExps"]["Message"], msg)
    
    def isCommand(self, msg):
        return re.match(self.config["RegExps"]["Command"].format(prefix=self.config["General"]["Prefix"]), msg)
    
    def addScenario(self, link):
        name = ""
        for item in link.split("/"):
            if re.match(r"(.*)\.[oc][c4]s",item):
                name = item
                break
        
        site = urllib.request.urlopen(link).read() #WARNING: Raises an error if the link is invalid!
        with open(os.path.join(self.path, name),"wb") as fobj:
            fobj.write(site)
        
        try:
            self.scenlist.index(name)
        except Exception:
            self.scenlist.append(name)
        return self
    
    def writeToServer(self, text : str) -> None:
        if not self.clonk:
            return
        
        elif self.clonk.stdin:
            self.clonk.stdin.write(f"{text}\n")
            self.clonk.stdin.flush()
    
    def setTopic(self, text=None) -> None:
        if not self.irc:
            return
        
        if self.topic != text:
            self.topic = text
            channel = self.config["Channels"]["Ingame"]
            self.irc.writeln(f"TOPIC {self.config['Channels']['Ingame']} :{text}")
    
    def shutdown(self):
        if self.shutdowned:
            return
        
        del self.updater
        
        if self.clonk and self.clonk.stdin and not self.clonk.stdin.closed:
            self.clonk.stdin.close()
        
        with open(self.config_path, "w") as fobj:
            self.config.write(fobj)
            print("Config file saved.")
        
        with open(os.path.join(self.path, "scenarios.lst"), "w") as fobj:
            fobj.writelines(self.scenlist)
        
        with open(os.path.join(self.path, "scenarios_league.lst"), "w") as fobj:
            fobj.writelines(self.league_scenlist)
        
        print("Scenario lists saved.")
        self.setTopic("Kein laufendes Spiel.")
        self.shutdowned = True
    
    def on(self, e):
        def process(f):
            signal(e).connect(f)
            return f
        return process

# Usage: ./pycrctrl.py path config
if len(sys.argv) <= 1:
    print("Usage: pycrctrl.py <path> <config file>")
    sys.exit(-1)

if sys.argv[1] == sys.argv[2] == "dummy":
    print("Dummy")
    sys.exit(0)

server = PyCRCtrl(sys.argv[1], sys.argv[2])

@server.irc.on("message")
def on_message(message, user, target, text):
    channel = server.config["Channels"]["Ingame"]
    if target == channel and server.ingamechat == "aktiviert" and user.nick != server.config["IRC"]["Nick"]:
        server.writeToServer(f"[IRC]<{user.nick}> {text}")

@server.irc.on("addressed")
def on_addressed(message, user, target, text):
    if target == server.config["Channels"]["Ingame"] and server.ingamechat == "aktiviert":
        return
    
    def reply(text):
        server.irc.say(target, text)
    
    try:
        server.checkForCommands(f"<{user}> {server.config['General']['Prefix']}{text}", reply=reply)
    except Exception as e:
        traceback.print_exc()

@server.on("cmd-start")
def start(args):
    server.stopped = False
    try:
        time = int(args[1])
    except Exception:
        time = 5
    args[0](f"/start {time}")

@server.on("cmd-stop")
def stop(args):
    def stopping():
        while server.clonk and server.stopped:
            server.writeToServer("/start 60000")
            sleep(100)
    
    if server.stopped == False:
        server.stopped = True
        threading.Thread(target=stopping).start()

@server.on("cmd-queue")
def queue(args):
    reply = args[0]
    reply("Warteschlange:")
    for i, scen in enumerate(server.queue.queue, start=1):
        reply(f"{i}. {scen}")

@server.on("cmd-list")
def lst(args):
    reply = args[0]
    if reply != server.writeToServer:
        reply("Die Szenarienliste kann nur ingame angesehen werden!")
        return
    
    reply("Verfügbare Szenarien:")
    for scen in server.scenlist:
        reply(scen)

@server.on("cmd-irc")
def cmd_irc(args):
    reply = args[0]
    if not args:
        reply("Keine Parameter angegeben!")
    
    if args[1] == "ingamechat":
        if len(args) <= 1 or args[2] == "off":
            server.ingamechat = "deaktivert"
        elif args[2] == "on":
            server.ingamechat = "aktiviert"

@server.on("cmd-host")
def host(args):
    reply = args[0]
    if len(args) <= 1:
        reply("Bitte gib einen Szenarionamen an!")
    scenario = args[1].strip()
    
    if scenario == "random":
        scenario = random.choice(server.scenlist).strip()
    
    elif scenario not in server.scenlist:
        reply(f"Szenario {scenario} nicht gefunden!")
    
    if not server.server_thread:
        server.scenario = scenario
        server.server_thread = threading.Thread(target=server.startClonk)
        server.server_thread.start()
        reply(f"Szenario {scenario} wird jetzt gehostet.")
    
    elif not server.queue.full():
        server.queue.put(scenario)
        reply(f"Szenario {scenario} wurde der Warteschlange hinzugefügt.")
    
    else:
        reply("Warteschlange ist voll!")

@server.on("cmd-quit")
def quit(args):
    reply = args[0]
    if server.clonk and server.clonk.stdin:
        server.clonk.stdin.close()
        server.server_thread.terminate()
        server.shutdown()
        sleep(5)
        raise SystemExit

try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    sys.exit(0)
