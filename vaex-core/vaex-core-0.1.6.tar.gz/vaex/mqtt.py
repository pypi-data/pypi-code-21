__author__ = 'maartenbreddels'
import sys
import json
import paho.mqtt.client as mqtt


def main(argv):


	type = argv[1]

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(client, userdata, flags, rc):
		print("Connected with result code "+str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		if type == "listen":
			client.subscribe("vaex/#")

	# The callback for when a PUBLISH message is received from the server.
	def on_message(client, userdata, msg):
		print(msg.topic+" "+str(msg.payload))

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect("broker.hivemq.com", 1883, 60)

	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	if type == "listen":
		client.loop_forever()
	else:
		client.loop_start()
		print(client.publish("vaex/zoom", json.dumps({'x':1, 'y':2, }), 2, False))

if __name__ == "__main__":
	main(sys.argv)