#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import glob
import asyncio
from concurrent import futures
import numpy as np
import cryio
from ..bcommon import compressor, default
from . import interface
from .integrator import Integrator


class PeriodicTask:
    def __init__(self, func):
        self.func = func
        self.stopped = True
        self.running = False

    def start(self, interval):
        self.interval = interval
        self.running = True
        asyncio.ensure_future(self._run())

    async def _run(self):
        self.stopped = False
        while self.running:
            self.func()
            await asyncio.sleep(self.interval)
        self.stopped = True

    def stop(self):
        self.running = False

    async def stopping(self):
        while not self.stopped:
            await asyncio.sleep(self.interval)


class Watcher:
    def __init__(self, typ='waxs'):
        self.interface = interface.Isaxs() if typ == 'saxs' else interface.Iwaxs()
        self._path = ''
        self._threads = 0
        self.runLocally = False
        self._multicolumnName = ''
        self.all = 0
        self.watchdog = PeriodicTask(self.checkFiles)
        self._loop = asyncio.get_event_loop()
        self.__integrator = Integrator()
        self.setPool()
        self.clearState()

    def clearState(self):
        self.results = {
            'imageFile': '',
            'chiFile': '',
            'transmission': 0,
            'data1d': None,
            'image': None,
            'timestamp': time.time(),
            'sent': True,
        }
        self.errors = []
        self.warnings = []
        self.taken = set()
        self.multicolumn = []
        self.qvalues = None
        self.all = 0
        self.interface.clearState()
        self.generate_response()

    @property
    def path(self):
        return self._path if self._path else 'unknown'

    @path.setter
    def path(self, path):
        if self._path == path:
            return
        elif not os.path.exists(path):
            self.errors.append(f'The {self.interface.type} path "{path}" does not exist')
        elif not os.path.isdir(path):
            self.errors.append(f'The {self.interface.type} path "{path}" is not a folder')
        else:
            self._changePath(path)

    def _changePath(self, path):
        run = self.watchdog.running
        if run:
            self.stopWatching()
        self._path = path
        if run:
            self.runWatching()

    def runWatching(self):
        asyncio.ensure_future(self._runWatching())

    async def _runWatching(self):
        if not self.watchdog.running:
            self.clearState()
            await self._loop.run_in_executor(self._pool, self.interface.init)
            self.watchdog.start(default.WATCHDOG_CALL_TIMEOUT)

    def checkFiles(self):
        images = []
        for ext in cryio.extensions():
            images += glob.glob(os.path.join(self._path, f'*{ext}'))
        images = set(images)
        self.all = len(images)
        images -= self.taken
        if self.interface.speed and self.interface.sspeed:
            self.taken |= images
            for image in images:
                asyncio.ensure_future(self._integrate_in_thread(image))
        else:
            for image in images:
                if not self.watchdog.running:
                    return
                self.taken.add(image)
                asyncio.ensure_future(self.integrate(image))

    def _integrate_in_thread(self, image):
        return self._loop.run_in_executor(self._pool, self.__integrator, image, self.interface)

    async def integrate(self, image):
        results = await self._integrate_in_thread(image)
        if results:
            self.results = results
            self.resetSent()
            if self.multicolumnName:
                self.multicolumn.append((results['chiFile'], results['data1d'][1]))
                if self.qvalues is None:
                    self.qvalues = results['data1d'][0]

    def stopWatching(self):
        if self.watchdog.running:
            self.watchdog.stop()
            self.shutdown_tasks()
            if self.multicolumn:
                asyncio.ensure_future(self._loop.run_in_executor(None, self.save_multicolumn))

    def shutdown_tasks(self):
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def save_multicolumn(self):
        self.multicolumn.sort()
        arrays, header = [compressor.decompressNumpyArray(self.qvalues, not self.interface.pickle)], 'q '
        for fn, ar in self.multicolumn:
            arrays.append(compressor.decompressNumpyArray(ar, not self.interface.pickle))
            header += '{} '.format(os.path.basename(fn))
        outf = os.path.join(self._path, self.interface.subdir, default.MULTICOLUMN_NAME)
        np.savetxt(outf, np.array(arrays).transpose(), fmt='%.6e', header=header, comments='#')

    @property
    def multicolumnName(self):
        return self._multicolumnName

    @multicolumnName.setter
    def multicolumnName(self, name):
        self._multicolumnName = name or ''

    def setParameters(self, params):
        self.interface.errors = self.errors = []
        self.interface.warnings = self.warnings = []
        for param in params:
            setattr(self, param, params[param])
            setattr(self.interface, param, params[param])
        if 'stop' in params:
            self.stopWatching()
        if not self.errors and params.get('run', 0):
            self.runWatching()

    def state(self):
        return self.generate_response()

    def generate_response(self):
        self.response = {
            'running': self.watchdog.running,
            'chiFile': self.results['chiFile'],
            'path': self.path,
            'total': self.total(),
            'imageFile': self.results['imageFile'],
            'transmission': self.results['transmission'],
            'data1d': None,
            'image': None,
            'timestamp': self.results['timestamp'],
            'all': self.all,
        }
        if not self.results['sent']:
            if self.results['data1d'] is not None:
                self.response['data1d'] = self.results['data1d']
            if self.results['image'] is not None:
                self.response['image'] = self.results['image']
            self.results['sent'] = True
        return self.response

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self, n):
        if self._threads != n:
            self._threads = n
            self.setPool()

    def setPool(self):
        if self._threads <= 0:
            self._threads = os.cpu_count()
            if not self._threads:
                self._threads = default.DEFAULT_THREADS
        if self._threads > default.MAX_THREADS:
            print(f'To many threads ({self._threads}) are not supported, setting number of threads to '
                  f'{default.MAX_THREADS}')
            self._threads = default.MAX_THREADS
        print(f'Running integration in {self._threads} threads')
        self._pool = futures.ThreadPoolExecutor(self._threads)

    def resetSent(self):
        self.results['sent'] = False

    def total(self):
        return self.interface.counter
