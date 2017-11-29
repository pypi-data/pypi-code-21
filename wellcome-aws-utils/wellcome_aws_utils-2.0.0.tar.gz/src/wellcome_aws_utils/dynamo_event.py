from enum import Enum

from boto3.dynamodb.types import TypeDeserializer

from wellcome_aws_utils.exceptions import UnWellcomeException


def create_dynamo_events(event):
    for record in event['Records']:
        yield DynamoEvent(record)


class DynamoEventType(Enum):
    REMOVE, INSERT, MODIFY = range(3)


class DynamoEvent:
    def _set_event_type(self, record):
        if self.record['eventName'] == 'REMOVE':
            self.event_type = DynamoEventType.REMOVE
        elif self.record['eventName'] == 'INSERT':
            self.event_type = DynamoEventType.INSERT
        elif self.record['eventName'] == 'MODIFY':
            self.event_type = DynamoEventType.MODIFY
        else:
            raise UnWellcomeException(
                f'Unrecognised eventName found in {record}!'
            )

    def __init__(self, record):
        self.record = record

        try:
            self._set_event_type(record)
            self.event_source_arn = record['eventSourceARN']

            self._keys = record['dynamodb']['Keys']
            self._new_image = record['dynamodb'].get('NewImage')
            self._old_image = record['dynamodb'].get('OldImage')
        except KeyError as e:
            raise UnWellcomeException(
                f'{e} not found in {record}!'
            )

    @staticmethod
    def _deserialize_values(image):
        td = TypeDeserializer()
        return {k: td.deserialize(v) for k, v in image.items()}

    def keys(self, deserialize_values=False):
        if deserialize_values and self._keys:
            return DynamoEvent._deserialize_values(self._keys)

        return self._keys

    def new_image(self, deserialize_values=False):
        if deserialize_values and self._new_image:
            return DynamoEvent._deserialize_values(self._new_image)

        return self._new_image

    def old_image(self, deserialize_values=False):
        if deserialize_values and self._old_image:
            return DynamoEvent._deserialize_values(self._old_image)

        return self._old_image
