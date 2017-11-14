import boto3

class IoTData(object):
    def __init__(self):
        self.client = boto3.client('iot-data')

    def publish(self, topic, payload, qos=1):
        """The message will be sent at least once"""
        return self.client.publish(
            topic=topic,
            qos=qos,
            payload=payload
        )