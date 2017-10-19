import paho.mqtt.client as mqtt
import json

class MQTTClient:

    def __init__(self, APPID, APPEUI, DEVID, PSW):
        self.client = mqtt.Client()
        self.APPID = APPID
        self.APPEUI = APPEUI
        self.PSW = PSW
        self.DEVID = DEVID
        self.bufferMSG = []

    def connect(self):
        self.client.username_pw_set(self.APPID, self.PSW)
        self.client.connect('eu.thethings.network', 1883, 60)

    def onConnect(self, userdata, flags, rc):
        self.client.subscribe('+/devices/+/up'.format(self.APPEUI))

    def onMessage(self, userdata, msg):
        j_msg = json.loads(msg.payload.decode('utf-8'))
        self.bufferMSG.append(j_msg)
        print('msg: ', j_msg)

    def onPublish(self, userdata, mid):
        print('MSG PUBLISHED', mid)

    def setBehavior(self, connect=onConnect, message=onMessage, publish=onPublish):
        self.client.on_connect = connect
        self.client.on_publish = publish
        self.client.on_message = message

    def start(self):
        print('LOOP STARTED')
        self.client.loop_forever()

    def startBackground(self):
        print('LOOP STARTED BACKGROUND')
        self.client.loop_start()

    def stopBackground(self):
        print('LOOP STOPPED BACKGROUND')
        self.client.loop_stop()
        self.client.disconnect()

    def stop(self):
        print('LOOP STOPPED')
        self.client.disconnect()

    def publish(self, msg):
        self.client.publish(self.APPID+'/devices/'+self.DEVID+'/down', msg)
