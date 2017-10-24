import socket
#import os
#import errno
from time import sleep
import time
from threading import RLock
from threading import Thread
from threading import Event
from Queue import Queue
import logging, logging.handlers
#import atexit

from digimat.lp import PacketManager, LP, UP


kLP_ST=20
kLP_EBUS=0xA1

kEBU_PING=0
kEBU_PONG=1
kEBU_READITEMS=10
kEBU_READITEM_RESPONSE=11
kEBU_WRITEITEM=12
kEBU_BROWSEITEMS=13
kEBU_BROWSEITEM_RESPONSE=14
kEBU_SUBSCRIBE=20

UNIT_STR = [ "V", "C", "Pa", "kPa", "%", "l/h", "bar", "Hz", \
    "s", "ms", "min", "kW", "kWh", "J", "kJ", "", \
    "m/s", "'", "h", "MWh", "MJ", "GJ", "W", "MW", \
    "kJ/h", "MJ/h", "GJ/h", "ml", "l", "m3", "ml/h", "m3/h" \
    "Wh", "?", "K", "", "lx", "t/min", "kvar", "kvarh", \
    "mbar", "msg/m", "m", "kJ/kg", "g/kg", "ppm", "A", "kVA",
    "kVAh", "ohm" ]


class EBusChannel(object):
    def __init__(self, host, port, logger):
        self._host=host
        self._port=port
        self._socket=None
        self._connected=False
        self._logger=logger
        self._timeoutInhibit=3.0

    @property
    def logger(self):
        return self._logger

    def connect(self):
        try:
            if not self._connected:
                if time.time()>=self._timeoutInhibit:
                    self._socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._socket.settimeout(10)
                    self._socket.connect((self._host, self._port))
                    self._socket.settimeout(0)
                    self._connected=True
                    self._timeoutInhibit=time.time()+5
                    self.logger.info("EBusChannel::Connected!")
                else:
                    self.logger.warning("EBusChannel::connection still inhibited!")
        except:
            self.logger.error("EBusChannel::connect Error!")
            self._timeoutInhibit=time.time()+5

    def isConnected(self):
        return self._connected

    def disconnect(self):
        try:
            self._socket.close()
        except:
            pass
        self.logger.info("EBusChannel::Disconnected!")
        self._connected=False

    def write(self, data):
        try:
            self.connect()
            self._socket.send(data)
        except:
            self.logger.error("EBusChannel::write error!")
            self.disconnect()

    def read(self):
        try:
            self.connect()
            data = self._socket.recv(4096)
            if not data:
                self.disconnect()
            return data
        except:
            pass


class EBusItem(object):
    def __init__(self, items, index, name, logger):
        if not name:
            name='io%d' % index
        self._items=items
        self._logger=logger
        self._lock=RLock()
        self._index=index
        self._name=name
        self._data=0xFFFF
        self._value=0.0
        self._unit=0xFF
        self._stampRefresh=0
        self._dead=1
        self._input=True
        self._updated=False
        self._triggerSignalChange=0
        self._triggerSignalChangeDelta=0
        self._triggerSignalChangeLastValue=0

    def isInput(self):
        return self._input

    def isOutput(self):
        return not self._input

    def isDead(self):
        return self._dead

    def isAlive(self):
        if not self.isDead():
            return True

    def signalDead(self):
        self._dead+=1

    @property
    def logger(self):
        return self._logger

    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name

    def getXmlConfig(self, station, label, labelLow='', labelNormal='', labelHigh='', decimals=1, modeImport=True, defaultValue=None, initValue=0, timeout=15):
        sxml='<BaseObject category="RSBEBI" station="%d" number="%d">\n' % (int(station), int(self.index))

        sxml+='<General mainLabel="%s" mainLabelLow="%s" mainLabelNormal="%s" mainLabelHigh="%s" decimals="%d"/>\n' % (label or '',
            labelLow or '',
            labelNormal or '',
            labelHigh or '',
            int(decimals))

        cfgImport='False'
        if modeImport:
            cfgImport='True'

        cfgDefaultValue='False'
        if defaultValue is not None:
            cfgDefaultValue='True'
            defaultValue=float(defaultValue)
        else:
            defaultValue=0

        sxml+='<RSCBEBI installed="1" wIdPeer="0" import="%s" applyDefaultValue="%s" fDefaultValue="%f" fInitValue="%f" chTimeout="%d" ' % (cfgImport,
            cfgDefaultValue, defaultValue, initValue, int(timeout))
        sxml+='/>\n'

        sxml+='</BaseObject>\n'
        return sxml

    def setDeltaSignalChange(self, delta):
        self._triggerSignalChangeLastValue=self._value
        if delta<0:
            delta=0
        self._triggerSignalChangeDelta=delta
        self._triggerSignalChange=0

    @property
    def delta(self):
        return self._triggerSignalChangeDelta
    @delta.setter
    def delta(self, value):
        self.setDeltaSignalChange(value)

    @property
    def value(self):
        with self._lock:
            return self._value
    @value.setter
    def value(self, value):
        with self._lock:
            if value is None:
                self.signalDead()
            else:
                if self._unit==15:
                    if value:
                        value=100.0
                    else:
                        value=0.0
                self._dead=0
                if value != self._value:
                    self._value = value
                    self._updated=True
                    if self.isOutput():
                        if self._unit==15:
                            self._triggerSignalChange=1
                            self._triggerSignalChangeLastValue=self._value
                        else:
                            if self._triggerSignalChangeDelta>0:
                                if abs(self._value-self._triggerSignalChangeLastValue)>=self._triggerSignalChangeDelta:
                                    self._triggerSignalChange=1
                                    self._triggerSignalChangeLastValue=self._value
                    self._items.onItemUpdate(self, value)
    @property
    def unit(self):
        with self._lock:
            return self._unit
    @unit.setter
    def unit(self, unit):
        with self._lock:
            if unit != self._unit:
                self._unit = unit
                self._updated=True
                self._items.onItemUpdate(self, self.value)

    def isTriggerSignalChange(self):
        return self._triggerSignalChange

    def age(self):
        with self._lock:
            return time.time()-self._stampRefresh

    def isPending(self, maxAge=30):
        if self.isInput():
            if self.age()>=maxAge:
                return True
        else:
            if not self.isDead():
                return self._updated or self.age()>=maxAge

    def clearPending(self):
        with self._lock:
            self._updated=False
            self._triggerSignalChange=0
            self._stampRefresh=time.time()

    def unitstr(self):
        try:
            return UNIT_STR[self.unit]
        except:
            return ''

    def valuestr(self):
        unit=self.unit
        if unit in [15, 0xFF]:
            return '%.0f' % self.value
        return '%.01f%s DEAD=%d' % (self.value, self.unitstr(), self._dead)

    def __str__(self):
        return self.valuestr()


class EBusInputItem(EBusItem):
    def __init__(self, items, index, name, logger):
        super(EBusInputItem, self).__init__(items, index, name, logger)
        self._input=True
        self._stampSubscribe=0

    def isSubscribePending(self):
        if self._triggerSignalChangeDelta>0:
            if time.time()-self._stampSubscribe>=60:
                return True

    def clearPendingSubscribe(self):
        with self._lock:
            self._stampSubscribe=time.time()

    def dump(self):
        with self._lock:
            print("<--i%d(%s)=%s" % (self.index, self.name, self.valuestr()))


class EBusOutputItem(EBusItem):
    def __init__(self, items, index, name, logger):
        super(EBusOutputItem, self).__init__(items, index, name, logger)
        self._input=False

    def dump(self):
        with self._lock:
            print("-->o%d(%s)=%s" % (self.index, self.name, self.valuestr()))


# http://stackoverflow.com/questions/1581895/how-check-if-a-task-is-already-in-python-queue
class UniqueQueue(Queue):
    def put(self, item, block=True, timeout=None):
        if item not in self.queue: # fix join bug
            Queue.put(self, item, block, timeout)

    def _init(self, maxsize):
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()


class EBusItems(object):
    def __init__(self, ebus, logger):
        self._logger=logger
        self._lock=RLock()
        self._ebus=ebus
        self._items={}
        self._itemsIndexByName={}
        self._inputs={}
        self._outputs={}
        self._timeoutInhibit=0
        self._queueItemUpdate=UniqueQueue()

    @property
    def logger(self):
        return self._logger

    @property
    def ebus(self):
        return self._ebus

    @property
    def packetManager(self):
        return self.ebus.packetManager

    def get(self, index):
        try:
            return self._items[index]
        except:
            pass

    def getFromName(self, name):
        try:
            return self._itemsIndexByName[name.lower()]
        except:
            pass

    def inputs(self):
        with self._lock:
            return self._inputs.values()

    def outputs(self):
        with self._lock:
            return self._outputs.values()

    def createInput(self, index, name, signalChangeDelta=0):
        with self._lock:
            item=self.get(index)
            if not item:
                item=EBusInputItem(self, index, name, self._logger)
                item.setDeltaSignalChange(signalChangeDelta)
                self._items[index]=item
                self._inputs[index]=item
                if name:
                    self._itemsIndexByName[name.lower()]=item
                self.logger.info("input %d:%s created" % (index, item.name))
            return item

    def createOutput(self, index, name, signalChangeDelta=0, unit=0xFF):
        with self._lock:
            item=self.get(index)
            if not item:
                item=EBusOutputItem(self, index, name, self._logger)
                item.setDeltaSignalChange(signalChangeDelta)
                item.unit=unit
                self._items[index]=item
                self._outputs[index]=item
                if name:
                    self._itemsIndexByName[name.lower()]=item
                self.logger.info("output %d:%s created" % (index, item.name))

                # let some time fixing value before sync
                self.inhibit(5.0)
            return item

    def manager(self):
        if time.time()>=self._timeoutInhibit:
            lp=self.packetManager.lp()

            with self._lock:
                for item in self.inputs():
                    if item.isPending():
                        self.packetManager.upReadItems(lp, item.index, 1)
                        item.clearPending()
                    if item.isSubscribePending():
                        self.packetManager.upSubscribe(lp, item.index, item.delta)
                        item.clearPendingSubscribe()

            with self._lock:
                for item in self.outputs():
                    if item.isPending():
                        self.packetManager.upWriteItem(lp, item.index, \
                            item.value, item.unit, \
                            item.isTriggerSignalChange())
                        item.clearPending()

            if lp._datasize>0:
                self.inhibit(2.0)
                lp.send()

    def inhibit(self, delay=1.0):
        t=time.time()+delay
        if t>self._timeoutInhibit:
            self._timeoutInhibit=t
            self.logger.debug('EBusItems manager inibited for %ds' % delay)

    def dump(self):
        for item in self.inputs():
            item.dump()
        for item in self.outputs():
            item.dump()

    def onItemUpdate(self, item, lastValue):
        self._queueItemUpdate.put(item, False)
        self.ebus.wakeup()

    def getUpdatedItem(self):
        try:
            return self._queueItemUpdate.get(False)
        except:
            pass


class EBusPacketManager(PacketManager):
    def __init__(self, lid, channel, logger):
        super(EBusPacketManager, self).__init__()
        self._logger=logger
        self._lid=lid
        self._channel=channel

    @property
    def channel(self):
        return self._channel

    @property
    def lid(self):
        return self._lid

    @property
    def logger(self):
        return self._logger

    def dispose(self):
        self.disconnect()
        super(EBusPacketManager, self).dispose()

    def write(self, data):
        return self.channel.write(data)

    def manager(self):
        data=self.channel.read()
        if data:
            self.receive(data)

    def lp(self, lptype=kLP_EBUS):
        return LP(lptype, self)

    def upReadItems(self, lp, index, count=1):
        up=lp.up(kEBU_READITEMS)
        up.writeWord(index)
        up.writeWord(count)
        up.store()
        self.logger.info("upReadItems(%d, %d)" % (index, count))
        return up

    def upBrowseItems(self, lp, pid):
        up=lp.up(kEBU_BROWSEITEMS)
        up.writeWord(pid)
        up.store()
        self.logger.debug("upBrowseItems(%d)" % (pid))
        return up

    def upWriteItem(self, lp, index, value, unit, signalChange=False):
        up=lp.up(kEBU_WRITEITEM)
        up.writeWord(self.lid)
        up.writeWord(index)
        up.writeFloat(value)
        up.writeByte(unit)
        up.writeBool(signalChange)
        up.store()
        self.logger.debug("upWriteItem(%d) %.1f (dV=%d)" % (index, value, signalChange))
        return up

    def upSubscribe(self, lp, index, dv):
        up=lp.up(kEBU_SUBSCRIBE)
        up.writeWord(index)
        up.writeFloat(dv)
        up.store()
        self.logger.debug("upSubscribe(%d, dv=%.1f)" % (index, dv))
        return up


class EBus(object):
    def __init__(self, lid, host, logServer='localhost', logLevel=logging.DEBUG):
        logger=logging.getLogger("EBUS(%d->%s)" % (lid, host))
        logger.setLevel(logLevel)
        socketHandler = logging.handlers.SocketHandler(logServer, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        self._logger=logger

        self._eventStop=Event()
        self._thread=Thread(target=self._manager)
        self._thread.daemon=True

        self._eventWakeup=Event()

        self._host=host
        self._port=5000
        self._lid=lid
        self._channel=EBusChannel(host, self._port, self._logger)
        self._packetManager=EBusPacketManager(lid, self._channel, self._logger)
        self._items=EBusItems(self, self._logger)
        self.registerHandlers()

        #todo: not functional but not yet found the good way to do it!
        # def _autostop():
        #     print("AUTOSTOP!")
        #     self.stop()
        #     atexit.unregister(_autostop)
        # atexit.register(_autostop)

        self.start()

    # def __enter__(self):
    #   pass

    # def __exit__(self):
    #   self.stop()

    def __del__(self):
        self.stop()
        self.disconnect()

    @property
    def logger(self):
        return self._logger

    @property
    def packetManager(self):
        return self._packetManager

    @property
    def lid(self):
        return self._lid

    def wakeup(self):
        self._eventWakeup.set()

    def sleep(self, timeout):
        if self._eventWakeup.wait(float(timeout)):
            self._eventWakeup.clear()
            return True

    def addPacketHandler(self, lptype, uptype, handler):
        return self.addHandler(lptype, uptype, handler)

    def registerHandlers(self):
        self.packetManager.addHandler(kLP_EBUS, kEBU_PONG, self.onPong)
        self.packetManager.addHandler(kLP_EBUS, kEBU_READITEM_RESPONSE, self.onReadItemResponse)
        self.packetManager.addHandler(kLP_EBUS, kEBU_BROWSEITEM_RESPONSE, self.onBrowseItemResponse)

    def ping(self):
        lp=self.packetManager.lp()
        up=lp.up(kEBU_PING)
        up.store()
        lp.send()

    def onPong(self, up):
        pass

    def onReadItemResponse(self, up):
        pid=up.readWord()
        index=up.readWord()
        value=up.readFloat()
        unit=up.readByte()
        item=self._items.get(index)
        if item:
            item.value=value
            item.unit=unit

    def discover(self):
        self._items.inhibit(3.0)
        self.browseItems(self.lid)

    def browseItems(self, pid=-1):
        if pid<0:
            pid=self.lid
        lp=self.packetManager.lp()
        self.packetManager.upBrowseItems(lp, pid)
        lp.send()

    def onBrowseItemResponse(self, up):
        index=up.readWord()
        pid=up.readWord()
        data=up.readWord()
        typeImport=bool(up.readByte())
        timeout=up.readByte()
        value=up.readFloat()
        unit=up.readByte()
        item=self.item(index)
        if not item:
            if typeImport:
                self.logger.debug('found unmapped peer i%d[id=%d, data=%d, timeout=%d]' % (index, pid, data, timeout))
                item=self.createOutput(index)
            else:
                self.logger.debug('found unmapped peer o%d[id=%d, data=%d, timeout=%d]' % (index, pid, data, timeout))
                item=self.createInput(index)
            try:
                item.value=value
                item.unit=unit
            except:
                pass

    def connect(self):
        if not self._channel.isConnected():
            self._channel.connect()
            self.ping()

    def disconnect(self):
        self._channel.disconnect()

    def createInput(self, index, name='', signalChangeDelta=0):
        if not name:
            name='i%d' % index
        return self._items.createInput(index, name, signalChangeDelta)

    def i(self, index, name='', signalChangeDelta=0):
        return self.createInput(index, name, signalChangeDelta)

    def createOutput(self, index, name='', signalChangeDelta=0, unit=0xFF):
        if not name:
            name='o%d' % index
        return self._items.createOutput(index, name, signalChangeDelta, self.guessUnit(unit))

    def createBoolOutput(self, index, name):
        return self.createOutput(index, name, 0.5, 15)

    def o(self, index, name='', signalChangeDelta=0, unit=0xFF):
        return self.createOutput(index, name, signalChangeDelta, unit)

    def inputs(self):
        return self._items.inputs()

    def outputs(self):
        return self._items.outputs()

    def item(self, index):
        return self._items.get(index)

    def itemFromName(self, name):
        return self._items.getFromName(name)

    def __getitem__(self, key):
        return self.item(int(key))

    def dump(self):
        self._items.dump()

    def waitForExit(self):
        self.stop()
        self.logger.debug("wait for thread termination")
        self._thread.join()
        self.logger.info("done")
        self.disconnect()

    def start(self):
        self.logger.debug("starting manager thread")
        self._thread.start()

    def _manager(self):
        self.logger.info("manager thread started")
        while not self._eventStop.isSet():
            try:
                self._items.manager()
                self._packetManager.manager()
            except SystemExit as e:
                # todo: probably never coming in subprocess, only in main thread
                self.logger.warning("manager thread halted by sys.exit() exception")
                self.stop()
            except:
                self.logger.exception("manager thread exception occured within manager()")
            time.sleep(0.2)

        self.logger.info("manager stopped")
        if not self._eventStop.isSet():
            self.logger.error("unsollicited manager stop!")
            self.stop()

    def stop(self):
        self._eventWakeup.set()
        if not self._eventStop.isSet():
            self._eventStop.set()
            self.logger.debug("stop request!")

    def isRunning(self):
        return not self._eventStop.isSet()

    def getUpdatedItem(self):
        return self._items.getUpdatedItem()

    def guessUnit(self, unit):
        if type(unit)=='int':
            return unit
        try:
            self._units
        except:
            self._units=[x.lower() for x in UNIT_STR]

        try:
            return self._units.index(unit.lower())
        except:
            pass

        return 0xff


if __name__=='__main__':
    pass
