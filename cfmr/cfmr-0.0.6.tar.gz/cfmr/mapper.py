from .emitter import Emitter
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

s3 = boto3.resource('s3')

def handle(event, ctx, mapperFunction):
    logger.debug('got event{}'.format(event))

    em = Emitter(
        ctx.client_context.custom['outputBucket'],
        ctx.client_context.custom['outputPrefix'],
        ctx.client_context.custom['jobId'],
        "mapper"
    )

    mapKey = event['key']
    inputBucket = ctx.client_context.custom['inputBucket']

    obj = s3.Object(inputBucket, mapKey)
    dataObj = obj.get()['Body'].read()
    logger.debug('dataObjType{}'.format(dataObj))
    mapperResult = mapperFunction(mapKey, dataObj, em)
    logger.debug('mapperResult{}'.format(mapperResult))
    em.flushEmits()

    return {
        'mapperResult': mapperResult
    }