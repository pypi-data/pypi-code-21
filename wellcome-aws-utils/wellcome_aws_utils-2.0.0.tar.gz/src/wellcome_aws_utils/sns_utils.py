# -*- encoding: utf-8 -*-

import collections
import datetime
import decimal
import json
import warnings

from wellcome_aws_utils.exceptions import UnWellcomeException

SNSEvent = collections.namedtuple('SNSEvent', 'subject message')


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, decimal.Decimal):
            if float(obj).is_integer():
                return int(obj)
            else:
                return float(obj)

        return json.JSONEncoder.default(self, obj)


def publish_sns_message(sns_client,
                        topic_arn,
                        message,
                        subject="default-subject"):
    """
    Given a topic ARN and a series of key-value pairs, publish the key-value
    data to the SNS topic.
    """
    response = sns_client.publish(
        TopicArn=topic_arn,
        MessageStructure='json',
        Message=json.dumps({
            'default': json.dumps(
                message,
                cls=EnhancedJSONEncoder
            )
        }),
        Subject=subject
    )

    print(f'SNS response = {response!r}')
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200

    return response


def extract_sns_messages_from_lambda_event(event):
    """
    Extracts a JSON message from an SNS event sent to an AWS Lambda.

    :param event: An event sent to a Lambda from SNS.
    :returns: A generator of SNSEvent instances.

    """
    if 'Records' not in event:
        raise UnWellcomeException(f'No records found in {event}')

    for record in event['Records']:
        if record['EventSource'] != 'aws:sns':
            raise UnWellcomeException(f'Invalid message source for {record}')

        try:
            subject = record['Sns']['Subject']
            message = json.loads(record['Sns']['Message'])
        except KeyError as e:
            raise UnWellcomeException(
                f'Invalid message structure, missing {e} in {record}'
            )

        yield SNSEvent(subject=subject, message=message)


def extract_json_message(event):
    """
    Extracts a JSON message from an SNS event sent to a lambda

    Deprecated in favour of extract_sns_messages_from_lambda_event
    """
    warnings.warn(
        'Deprecated in favour of extract_sns_messages_from_lambda_event',
        DeprecationWarning
    )

    message = event['Records'][0]['Sns']['Message']
    return json.loads(message)
