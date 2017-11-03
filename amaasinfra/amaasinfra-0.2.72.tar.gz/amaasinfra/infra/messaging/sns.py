import boto3


class SNS(object):
    """
    This class is to process the notifications by using SNS service
    """
    def __init__(self, region=''):
        if region:
            self._sns = boto3.client('sns', region_name=region)
        else:
            self._sns = boto3.client('sns')

    def publish(self, topic_arn, subject, message):
        """
        Publish messages to SNS
        """
        return self._sns.publish(TopicArn=topic_arn,
                                 Subject=subject,
                                 Message=message)