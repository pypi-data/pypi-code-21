from .emitter import Emitter
from functools import reduce
import logging
import boto3
import json


logger = logging.getLogger()

s3 = boto3.resource('s3')

def handle(event, ctx, reducerFunction):
    logger.debug('got event{}'.format(event))

    em = Emitter(
        ctx.client_context.custom['outputBucket'],
        ctx.client_context.custom['outputPrefix'],
        ctx.client_context.custom['jobId'],
        "reducer"
    )

    reducerKey = event['key']
    outputBucket = ctx.client_context.custom['outputBucket']

    # TODO use parallel fetching
    def getData(path):
        obj = s3.Object(outputBucket, path)
        return json.loads(obj.get()['Body'].read().decode('utf-8'))

    # get items for this partition
    allData = list(map(getData, event['value']))
    logger.debug(f"allData: {allData}")

    # decode data
    def decodeData(allValues, jsonData):
        values = jsonData['values']
        for v in values:
            if(v['valueIsBase64']):
                allValues.append(codecs.decode(v['value'], 'base64'))
            else:
                allValues.append(v['value'])
        return allValues

    values = reduce(decodeData, allData, [])

    # decode key
    key = allData[0]['key']
    if(allData[0]['keyIsBase64']):
        key = codecs.decode(key, 'base64')

    # run reducer
    reducerResult = reducerFunction(key, values, em)
    logger.debug('reducerResult{}'.format(reducerResult))
    em.flushEmits()

    return {
        'reducerResult': reducerResult
    }
