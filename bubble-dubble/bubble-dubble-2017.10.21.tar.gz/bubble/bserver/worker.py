#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
import pickle
import struct
import asyncio
from ..bcommon.default import PICKLE_HEADER_STRUCT, PICKLE_MAGIC_NUMBER
from .watcher import Watcher


class BubbleWorker:
    def __init__(self):
        self.startedTimestamp = time.time()
        self.killed = False
        self._pickle = False
        self.runLocally = False
        self.waxsWatcher = Watcher('waxs')
        self.saxsWatcher = Watcher('saxs')
        self.pardict = {
            'kill': self.kill,
            'state': self.state,
            'saxs': self.saxs,
            'waxs': self.waxs,
            'pickle': self.pickle,
        }

    def pickle(self, request):
        self._pickle = request
        return {}

    def saxs(self, request):
        return self.setIntegrator(request, self.saxsWatcher)

    def waxs(self, request):
        return self.setIntegrator(request, self.waxsWatcher)

    # noinspection PyUnusedLocal
    def kill(self, request=None):
        loop = asyncio.get_event_loop()
        loop.call_soon(self.saxsWatcher.stopWatching)
        loop.call_soon(self.waxsWatcher.stopWatching)
        loop.call_later(0.5, loop.stop)
        self.killed = True
        return {}

    # noinspection PyUnusedLocal
    def state(self, request=None):
        return {
            'server': self.stateServer(),
            'saxs': self.stateSAXS(),
            'waxs': self.stateWAXS(),
        }

    def stateSAXS(self):
        state = self.saxsWatcher.state()
        if self.killed:
            state['running'] = False
        return state

    def stateWAXS(self):
        state = self.waxsWatcher.state()
        if self.killed:
            state['running'] = False
        return state

    def stateServer(self):
        return {
            'startedTimestamp': self.startedTimestamp,
            'killed': self.killed,
        }

    def setIntegrator(self, params, watcherObject):
        params['pickle'] = self._pickle
        watcherObject.setParameters(params)
        state = {}
        if watcherObject.errors:
            state['errors'] = watcherObject.errors
        if watcherObject.warnings:
            state['warnings'] = watcherObject.warnings
        return state

    def parse(self, request):
        state = {}
        for key in request:
            if key in self.pardict:
                state.update(self.pardict[key](request[key] if key in request else None))
        return self.pack_state(state)

    def pack_state(self, state):
        if self._pickle:
            packet = pickle.dumps(state)
            header = struct.pack(PICKLE_HEADER_STRUCT, PICKLE_MAGIC_NUMBER, len(packet))
            return header + packet
        else:
            return '{}\r\n'.format(json.dumps(state)).encode()

    def resetSent(self):
        self.waxsWatcher.resetSent()
        self.saxsWatcher.resetSent()
