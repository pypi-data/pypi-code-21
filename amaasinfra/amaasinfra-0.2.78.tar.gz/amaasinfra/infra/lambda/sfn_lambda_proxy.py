"""
This lambda is used in Step Functions to invoke the lambdas in Singapore region that
performs the actual logic.
This is a temporary solution until Step Functions is available in Singapore region.
Currently this expects the lambdas to be invoked to specify the next step in the state machine.
Not ideal since it makes the specific steps aware of the execution chain but it greatly simplifies
the deployment
"""
import boto3
import logging
import json

logger = logging.getLogger()

def handler(event, context):
    next_lambda = event.get('next')
    # make the invoked lambda explicitly set this
    event['next'] = None

    if not next_lambda:
        error = 'The lambda function to invoke was not specified.'
        logger.error(error)
        raise RuntimeError(error)

    logger.info('Invoking {}'.format(next_lambda))
    client = boto3.client('lambda', region_name='ap-southeast-1')
    response = client.invoke(FunctionName=next_lambda, Payload=json.dumps(event))

    result = response.get('Payload')
    payload = result.read()
    # error = response.get('FunctionError')
    # error_message = error.read()

    # logger.info(error_message)
    # if error_message:
    #     raise RuntimeError(error_message)
    # todo: handle errors here
    return json.loads(payload)
