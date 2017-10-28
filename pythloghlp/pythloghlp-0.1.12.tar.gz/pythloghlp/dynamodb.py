# -*- coding: utf-8 *-*
import sys
import logging
import datetime
import boto3

if sys.version_info[0] >= 3:
    unicode = str

class DynamoFormatter(logging.Formatter):
    def format(self, record):
        data = record.__dict__.copy()
        if record.args:
            msg = record.msg % record.args
        else:
            msg = record.msg
        data.update(
            args=str([unicode(arg) for arg in record.args]),
            msg=str(msg)
        )
        if sys.version_info[0] >= 3:
            data = dict((k, v) for k, v in data.items() if v)
        else:
            data = dict((k, v) for k, v in data.iteritems() if v)
        if 'exc_info' in data and data['exc_info']:
            data['exc_info'] = self.formatException(data['exc_info'])
        return data

class DynamoHandler(logging.Handler):
    @classmethod
    def to(cls, table_name, aws_region, aws_access_key_id, aws_secret_access_key, level=logging.NOTSET):
        return cls(table_name, aws_region, aws_access_key_id, aws_secret_access_key, level)

    def __init__(self, table_name, aws_region, aws_access_key_id, aws_secret_access_key, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        #dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(table_name)
        self.formatter = DynamoFormatter()

    def emit(self, record):
        try:
            r = self.format(record)
            r['level'] = r['levelname']
            r['timestamp'] = str(datetime.datetime.now())[:23]
            del r['created']
            del r['msecs']
            del r['thread']
            del r['relativeCreated']
            del r['levelname']
            del r['args']
            del r['filename']
            del r['funcName']
            del r['levelno']
            del r['lineno']
            del r['module']
            del r['pathname']
            del r['process']
            del r['processName']
            del r['threadName']
            self.table.put_item(Item=r)
        except Exception as e:
            print("Unable to save log record: %s", e)