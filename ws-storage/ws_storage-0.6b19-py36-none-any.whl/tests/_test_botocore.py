import asyncio
import os
import sys

import botocore.session

sys.path.append(os.path.join(os.environ['HOME'], 'config'))
import aws

conf = aws.Conf

session = botocore.session.get_session()

client = session.create_client(
        's3', 
        region_name=conf.REGION,
        aws_secret_access_key=conf.SECRET_ACCESS_KEY,
        aws_access_key_id=conf.ACCESS_KEY_ID)

resp = client.put_object(
        Bucket=conf.BUCKET,
        Key='test',
        Body=b'hello')

print(resp)
print()

resp = client.get_object(
        Bucket=conf.BUCKET,
        Key='test')

print(resp)
print()


import aiobotocore

loop = asyncio.get_event_loop()

session = aiobotocore.session.get_session()

async def go():

    async with session.create_client(
            's3', 
            region_name=conf.REGION,
            aws_secret_access_key=conf.SECRET_ACCESS_KEY,
            aws_access_key_id=conf.ACCESS_KEY_ID) as client:

        resp = await client.put_object(
                Bucket=conf.BUCKET,
                Key='test',
                Body=b'hello')

        print(resp)
        print()
        
        resp = await client.get_object(
                Bucket=conf.BUCKET,
                Key='test')

        print(resp)
        print()

loop.run_until_complete(go())



