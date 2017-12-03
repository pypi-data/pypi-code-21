#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# gstplayer.py
# python module to play audio by gstreamer
#
# Copyright (C) 2017 Shiro Ninomiya
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst as gst
from time import time

class GstAplay(object):
    def __init__(self, adevice='hw:1,0', volume=1.0):
        GObject.threads_init()
        gst.init(None)
        self.adevice=adevice
        self.volume=volume
        self.__state=0 # 0:init, 1:ready to play, 2:playing

    def get_state(self):
        state_string=['init', 'ready', 'playing']
        return state_string[self.__state]

    def open(self, uri):
        if self.__state > 0 : self.close()
        try:
            self.pipeline=gst.Pipeline()
            playbin = gst.ElementFactory.make('playbin', 'playbin')
        except:
            print "can't create playbin: %s" % sys.exc_info()[0]
            return -1
        
        try:
            audiosink = gst.ElementFactory.make('alsasink', 'audiosink')
            audiosink.set_property('device', self.adevice)
        except:
            print "can't create audiosink: %s" % sys.exc_info()[0]
            return -1
        
        try:
            playbin.set_property('volume', self.volume)
            playbin.set_property('audio-sink', audiosink)
            playbin.set_property('uri', uri)
            self.pipeline.add(playbin)
        except:
            print "can't create pipeline: %s" % sys.exc_info()[0]
            return -1
        self.playbin=playbin
        self.__state=1
        self.playing_duration=0.0
        return 0

    def close(self):
        if self.__state < 1 : return
        self.pipeline.set_state(gst.State.NULL)
        self.pipeline.remove(self.playbin)
        self.__state=0
        self.playbin=None
        if self.playing_starttime:
            self.playing_duration=time()-self.playing_starttime
        return self.playing_duration

    def play(self):
        if self.__state < 1 or self.__state == 2: return
        self.pipeline.set_state(gst.State.PLAYING)
        self.playing_starttime=time()
        self.__state=2
        
    def pause(self):
        if self.__state < 2 : return
        self.pipeline.set_state(gst.State.PAUSED)
        self.playing_duration=time()-self.playing_starttime
        self.playing_starttime=0.0
        self.__state=1
        

if __name__ == "__main__":
    station="http://149.56.23.7:20176/stream" # set a sample to play
    gp = GstAplay()
    if gp.open(station): sys.exit(-1)
    while True:
        a=raw_input('p:play, s:stop, c:close ?>')
        if a=='c':
            gp.close()
            break;
        elif a=='p':
            gp.play()
        elif a=='s':
            gp.pause()
        else:
            print gp.get_state()
