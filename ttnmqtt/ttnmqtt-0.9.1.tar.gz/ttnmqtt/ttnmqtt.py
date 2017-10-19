import paho.mqtt.client as mqtt
from pydispatch import dispatcher
import json

class MQTTClient:

    def __init__(self, APPID, APPEUI, PSW, DEVID=None):
        self.__client = mqtt.Client()
        self.__APPID = APPID
        self.__APPEUI = APPEUI
        self.__PSW = PSW
        self._DEVID = DEVID
        self._buffer = []
        self._currentMSG = {}
        self._numberOfMsg = 0
        self._messageHandler = None

    def setDeviceID(self, devid):
        self._DEVID = devid

    def getLastMessage(self):
        return self._currentMSG

    def getAllMessages(self):
        return self._buffer

    def connect(self):
        self.__client.on_connect = self._onConnect()
        self.__client.on_publish = self._onPublish()
        self.__client.on_message = self._onMessage()
        self.__client.on_disconnect = self._onDisconnect()
        self.__client.username_pw_set(self.__APPID, self.__PSW)
        self.__client.connect('eu.thethings.network', 1883, 60)

    def customConnect(self, region, port=1883):
        self.__client.on_connect = self._onConnect()
        self.__client.on_publish = self._onPublish()
        self.__client.on_message = self._onMessage()
        self.__client.on_disconnect = self._onDisconnect()
        self.__client.username_pw_set(self.__APPID, self.__PSW)
        self.__client.connect(region+'.thethings.network', port, 60)

    def _onConnect(self):
        def on_connect(client, userdata, flags, rc):
            res = client.subscribe('+/devices/+/up'.format(self.__APPEUI))
            if(res[0]==0):
                print('CONNECTED AND SUBSCRIBED')
            else:
                print('ERROR CONNECTING')
        return on_connect

    def _onDisconnect(self):
        def on_disconnect(client, userdata, rc):
            if rc != 0:
                print('UNEXPECTED DISCONNECTION')
            else:
                print('DISCONNECTED')
        return on_disconnect

    def _onMessage(self):
        def on_message(client, userdata, msg):
            print('MESSAGE RECEIVED')
            j_msg = json.loads(msg.payload.decode('utf-8'))
            self._buffer.append(j_msg)
            self._currentMSG = j_msg
            self._numberOfMsg+=1
            dispatcher.send(signal='New Message', sender=self)
        return on_message

    def _onPublish(self):
        def on_publish(client, userdata, mid):
            print('MSG PUBLISHED', mid)
        return on_publish

    def setMessageBehavior(self, message):
        self.__client.on_message = message

    def setConnectBehavior(self, connect):
        self.__client.on_connect = connect

    def setPublishBehavior(self, publish):
        self.__client.on_publish = publish

    def setGlobalBehavior(self, connect, message, publish):
        self.__client.on_connect = connect
        self.__client.on_publish = publish
        self.__client.on_message = message

    def setMessageHandler(self, handler):
        if self._messageHandler:
            dispatcher.disconnect(self._messageHandler, signal='New Message', sender=dispatcher.Any)
        self._messageHandler = handler
        dispatcher.connect(self._messageHandler, signal='New Message', sender=dispatcher.Any)

    def start(self):
        print('LOOP STARTED')
        self.__client.loop_forever()

    def startBackground(self):
        print('LOOP STARTED BACKGROUND')
        self.__client.loop_start()

    def stopBackground(self):
        print('LOOP STOPPED BACKGROUND')
        self.__client.loop_stop()
        self.disconnect()

    def disconnect(self):
        self.__client.disconnect()

    def publish(self, msg):
        if(self._DEVID != None):
            result = self.__client.publish(self.__APPID+'/devices/'+self._DEVID+'/down', msg)
            print("Message will be published on the next uplink message")
        else:
            print('No DeviceID defined please use the setDeviceID method')
