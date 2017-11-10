import os
import boto3
import logging
import json
import codecs
import hashlib
import binascii
import inspect
from collections import defaultdict

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

s3 = boto3.resource('s3')

class Emitter(object):

    def __init__(self, outputBucket, outputPrefix, jobId, emitterType):
        self.emitBuffer = defaultdict(list)
        self.outputBucket = outputBucket
        self.outputPrefix = outputPrefix
        self.jobId = jobId
        self.emitterType = emitterType

    def emit(self, key, value):
        self.emitBuffer[key].append(value)

    def flushEmits(self):
        for key in self.emitBuffer:
            self.flushEmit(key, self.emitBuffer[key])

    def flushEmit(self, key, values):
        logger.debug(f"flushing {key}, {values}")
        keyIsBuffer = type(key).__name__ is 'bytes'
        outputKey = codecs.encode(key, 'base64') if keyIsBuffer else key

        allValues = []
        for v in values:
            valueIsBuffer = type(v).__name__ is 'bytes'
            outputValue = codecs.encode(v, 'base64') if valueIsBuffer else v
            value = {
                'value': outputValue,
                'valueIsBase64': valueIsBuffer,
            }
            allValues.append(value)

        # for S3 keys
        h = hashlib.sha256()
        if(keyIsBuffer):
            h.update(key)
        else:
            h.update(key.encode('utf-8'))
        partitionKey = h.hexdigest()
        partKey = str(binascii.hexlify(os.urandom(16)), 'ascii')

        flushKey = f"{self.outputPrefix}/{self.jobId}/{self.emitterType}/{partitionKey}/{partKey}"

        logger.debug(f"Flushing key: {key}, values: {allValues}, to s3://{self.outputBucket}/{flushKey}")

        body = {
          'key': outputKey,
          'keyIsBase64': keyIsBuffer,
          'values': allValues
        }
        obj = s3.Object(self.outputBucket, flushKey)
        obj.put(Body=json.dumps(body).encode('utf-8'))
