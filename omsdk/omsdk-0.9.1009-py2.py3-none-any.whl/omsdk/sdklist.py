#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Copyright � 2017 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its
# subsidiaries. Other trademarks may be trademarks of their respective owners.
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
# Authors: Vaideeswaran Ganesan
#
import os
import io
import logging
import threading
import json
import time
from omsdk.sdkconsole import iConsoleRegistry, iConsoleDriver, iConsoleDiscovery
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkproto import PCONSOLE
import sys
import logging


logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


#logging.basicConfig(level=logging.DEBUG,
#    format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class ListProc:
    def __init__(self, sd, listfile, creds):
        self.listfile = listfile
        self.myentitylistlock = threading.Lock()
        self.sd = sd
        self.creds = creds
        # SDK Infrastructure
        self.entitylist = []
        self.success = {}
        self.failed = {}

    def process(self):
        self.threadlist = []
        if not os.path.isfile(self.listfile):
            logger.debug("Unable to find file")
            return None
        counter = 0
        with open(self.listfile, "r") as mylist:
            for line in mylist:
                counter = counter + 1
                device = line.rstrip()
                thr = threading.Thread(name=device, \
                          target=self._worker, args=(device,str(counter),))
                self.threadlist.append(thr)
                thr.start()
        logger.debug('Waiting for _worker threads')
        for t in self.threadlist:
            t.join()
        return self


    def printx(self):
        with self.myentitylistlock:
            for device in self.entityjson["devices"]["Devices"]:
                logger.debug("-======" + str(device) + "----------")
                if not device is None:
                    logger.debug(PrettyPrint.prettify_json(device.entityjson))
                logger.debug("-==================-------")


    def _worker(self, device, counter):
        logger.debug("Starting")
        devEntity = self.sd.get_driver(self.sd.driver_enum.iDRAC, device, self.creds)
        with self.myentitylistlock:
            if not devEntity is None:
                self.entitylist.append(devEntity)

    def _run(self, entity, counter):
        t1 = time.time()
        if not entity is None:
            entity.get_entityjson()
            #entity.get_partial_entityjson(entity.ComponentEnum.System)
            with open('.\\output\\ff\\detailed.' + str(counter), 'w') as f:
                json.dump(entity.get_json_device(), f)
                f.flush()
        logger.debug("Time for " + str(counter) + " thread = " + str(time.time()-t1))
        logger.debug("Exiting")

    def get_data(self):
        counter = 0
        for entity in self.entitylist:
            counter = counter +1
            thr = threading.Thread(name=entity.ipaddr, \
                     target=self._run,\
                     args=(entity,counter,))
            self.threadlist.append(thr)
            thr.start()
        for t in self.threadlist:
            t.join()
