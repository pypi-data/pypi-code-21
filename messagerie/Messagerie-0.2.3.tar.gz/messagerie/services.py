import os
import re
import base64
import requests
from email.mime import multipart, text, application

from boto3 import client


class AWSEntity(object):
    __ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    __ACCESS_ID = os.environ['AWS_ACCESS_KEY_ID']
    __REGION = os.environ['AWS_REGION']
    __S3_BASE_URL = 'https://s3-us-west-2.amazonaws.com'

    @classmethod
    def create_bucket(cls, bucket_name, permission='public-read', region=os.environ['AWS_REGION']):
        try:
            s3 = client('s3', aws_secret_access_key=cls.__ACCESS_KEY,
                        aws_access_key_id=cls.__ACCESS_ID)
            return s3.create_bucket(ACL=permission, Bucket=bucket_name, CreateBucketConfiguration={
                'LocationConstraint': region
            })
        except Exception, e:
            raise e

    @classmethod
    def delete_bucket(cls, bucket_name):
        """
        delete s3 bucket matching bucket_name
        :param bucket_name
        :return
        """
        try:
            s3 = client('s3', aws_secret_access_key=cls.__ACCESS_KEY,
                        aws_access_key_id=cls.__ACCESS_ID)
            return s3.delete_bucket(Bucket='bucket_name')
        except Exception, e:
            raise e

    @classmethod
    def upload_b64(cls, base64_image, filename, bucket_name=os.environ.get('AWS_STORAGE_BUCKET_NAME')):
        """
        Upload base64 encoded image to s3
        :return:
        """
        try:
            s3 = client('s3', aws_secret_access_key=cls.__ACCESS_KEY,
                        aws_access_key_id=cls.__ACCESS_ID)
            _file = re.sub("data:image/jpeg;base64,", '', base64_image)
            s3.put_object(ACL='public-read', Bucket=bucket_name,
                                 Body=_file.decode('base64'), Key=filename)
            return '%s/%s/%s' % (cls.__S3_BASE_URL, bucket_name, filename)
        except Exception, e:
            raise e

    @classmethod
    def upload_file(cls, file_path, bucket_name=os.environ.get('AWS_STORAGE_BUCKET_NAME'), filename=None):
        """
        Upload base64 encoded image to s3
        :return:
        """
        try:
            s3 = client('s3', aws_secret_access_key=cls.__ACCESS_KEY,
                        aws_access_key_id=cls.__ACCESS_ID)
            if not os.path.isfile(file_path):
                raise Exception('Invalid file path')

            filename = filename if filename else os.path.basename(file_path)
            s3.upload_file(file_path, bucket_name, filename, ExtraArgs={'ACL': 'public-read'})
            return '%s/%s/%s' % (cls.__S3_BASE_URL, bucket_name, filename)
        except Exception, e:
            raise e

    @staticmethod
    def convert_to_b64(image_url):
        """
        base64 encodes an image url
        :param image_url:
        :return:
        """
        try:
            return base64.b64encode(requests.get(image_url).content)
        except Exception, e:
            raise e

    @classmethod
    def send_formatted_message(cls, sender, subject, to, text_body='', html_body='', cc=list(), bcc=list(),
                               reply_to=list()):
        """
        send formatted message using ses
        :return:
        """
        # validate email address
        if not cls.__validate_email(sender):
            raise Exception('Sender address not an email address')

        recipients = to if isinstance(to, (list, tuple)) else [to]
        invalid_recipients = filter(lambda x: not cls.__validate_email(x), recipients)
        if len(invalid_recipients) > 0:
            raise Exception('Invalid recipient addresses - {}'.format(invalid_recipients))

        cc_recipients = cc if isinstance(cc, (list, tuple)) else [cc]
        invalid_cc = filter(lambda x: not cls.__validate_email(x), cc_recipients)
        if len(invalid_cc) > 0:
            raise Exception('Invalid cc addresses - {}'.format(invalid_cc))

        bcc_recipients = bcc if isinstance(bcc, (list, tuple)) else [bcc]
        invalid_bcc = filter(lambda x: not cls.__validate_email(x), bcc_recipients)
        if len(invalid_bcc) > 0:
            raise Exception('Invalid bcc addresses - {}'.format(invalid_bcc))

        reply_to_recipients = reply_to if isinstance(reply_to, (list, tuple)) else [reply_to]
        invalid_reply_to = filter(lambda x: not cls.__validate_email(x), reply_to_recipients)
        if len(invalid_reply_to) > 0:
            raise Exception('Invalid reply-to addresses - {}'.format(invalid_reply_to))

        try:
            ses_client = client('ses', aws_secret_access_key=cls.__ACCESS_KEY,
                                aws_access_key_id=cls.__ACCESS_ID, region_name=cls.__REGION)

            msg = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text_body,
                        'Charset': 'UTF-8'
                    }
                }
            }

            if html_body:
                msg['Body']['Html'] = {
                    'Data': html_body,
                    'Charset': 'UTF-8'
                }
            response = ses_client.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': recipients,
                    'CcAddresses': cc_recipients,
                    'BccAddresses': bcc_recipients
                },
                Message=msg,
                ReplyToAddresses= reply_to_recipients
            )
            return response
        except Exception, e:
            raise e

    @staticmethod
    def __validate_email(email):
        regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[A-Za-z]+'
        return True if re.match(regex, email) else False

    @classmethod
    def send_raw_message(cls, sender, subject, body, recipients, is_html=False, cc=list(), bcc=list(), reply_to=list(),
                         file_paths=list()):
        """
        send raw message using ses
        :return:
        """
        # validate email address
        if not cls.__validate_email(sender):
            raise Exception('Sender address not an email address')

        recipients = recipients if isinstance(recipients, (list, tuple)) else [recipients]
        invalid_recipients = filter(lambda x: not cls.__validate_email(x), recipients)
        if len(invalid_recipients) > 0:
            raise Exception('Invalid recipient addresses - {}'.format(invalid_recipients))

        cc_recipients = cc if isinstance(cc, (list, tuple)) else [cc]
        invalid_cc = filter(lambda x: not cls.__validate_email(x), cc_recipients)
        if len(invalid_cc) > 0:
            raise Exception('Invalid cc addresses - {}'.format(invalid_cc))

        bcc_recipients = bcc if isinstance(bcc, (list, tuple)) else [bcc]
        invalid_bcc = filter(lambda x: not cls.__validate_email(x), bcc_recipients)
        if len(invalid_bcc) > 0:
            raise Exception('Invalid bcc addresses - {}'.format(invalid_bcc))

        reply_to_recipients = reply_to if isinstance(reply_to, (list, tuple)) else [reply_to]
        invalid_reply_to = filter(lambda x: not cls.__validate_email(x), reply_to_recipients)
        if len(invalid_reply_to) > 0:
            raise Exception('Invalid reply-to addresses - {}'.format(invalid_reply_to))

        msg = multipart.MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ','.join(map(str, recipients))

        if len(cc_recipients) > 0:
            msg['Cc'] = ','.join(map(str, cc_recipients))

        if len(bcc_recipients) > 0:
            msg['Bcc'] = ','.join(map(str, bcc_recipients))

        if len(reply_to_recipients) > 0:
            msg['Reply-To'] = ','.join(map(str, reply_to_recipients))

        if is_html:
            msg_html = text.MIMEText(body, 'html')
            msg_html.add_header('Content-Type', 'text/html; charset=UTF-8')
            msg.attach(msg_html)
        else:
            msg_body = text.MIMEText(body, 'plain')
            msg.attach(msg_body)

        if isinstance(file_paths, (list, tuple)):
            for file_path in file_paths:
                if os.path.isfile(file_path):
                    attachment = application.MIMEApplication(open(file_path, "rb").read())
                    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                    msg.attach(attachment)

        try:
            ses_client = client('ses', aws_secret_access_key=cls.__ACCESS_KEY,
                                aws_access_key_id=cls.__ACCESS_ID, region_name=cls.__REGION)

            response = ses_client.send_raw_email(
                RawMessage={
                     'Data': msg.as_string(),
                },
                Source=msg['From'],
                Destinations=recipients
            )
            return response
        except Exception, e:
            raise e

    @classmethod
    def set_identity_notification(cls, identity, notification_type, sns_topic_arn):
        """
        handling bounce and complaint ses
        :param identity: domain or email address identified as source for emails
        :param notification_type: 'Bounce'|'Complaint'|'Delivery'
        :param sns_topic_arn: sns topic arn
        :returns
        """
        try:
            ses_client = client('ses', aws_secret_access_key=cls.__ACCESS_KEY,
                                aws_access_key_id=cls.__ACCESS_ID, region_name=cls.__REGION)

            return ses_client.set_identity_notification_topic(Identity=identity, NotificationType=notification_type,
                                                              SnsTopic=sns_topic_arn)
        except Exception, e:
            raise e

    @classmethod
    def create_sns_topic(cls, topic_name):
        """
        creates sns topic
        :param topic_name
        :returns
        """
        try:
            sns_client = client('sns', aws_secret_access_key=cls.__ACCESS_KEY, regions_name=cls.__REGION,
                     aws_access_key_id=cls.__ACCESS_ID)
            return sns_client.create_topic(Name=topic_name)
        except Exception as e:
            raise e

    @classmethod
    def subscribe_to_sns_topic(cls, sns_topic_arn, protocol, endpoint):
        """
        subscribe to sns topic arn
        :param sns_topic_arn: combination of region name, customer name and topic name
        :param protocol: http|https|email|email-json|sms|sqs|application|lambda
        :param endpoint: dependent on protocol
        :returns
        """
        try:
            sns_client = client('sns', aws_secret_access_key=cls.__ACCESS_KEY, regions_name=cls.__REGION,
                                aws_access_key_id=cls.__ACCESS_ID)
            return sns_client.subscribe(TopicArn=sns_topic_arn, Protocol=protocol, Endpoint=endpoint)
        except Exception as e:
            raise e
