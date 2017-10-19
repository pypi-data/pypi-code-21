import asyncio
import botocore.session
import aiobotocore

TEST_BUCKET = 'chuck1-dummy1'
TEST_KEY = 'blah'
CREATE_REGION = 'eu-west-1'
QUERY_REGION = 'us-west-2'

create_client = botocore.session.get_session().create_client('s3', region_name=CREATE_REGION)

def boto_test():
    print('boto_test')
    session = botocore.session.get_session()

    client = session.create_client('s3', region_name=QUERY_REGION)

    resp = client.put_object(
            Bucket=TEST_BUCKET,
            Key=TEST_KEY,
            Body=b'hello')

    print(resp)
    print()

    resp2 = client.get_object(
            Bucket=TEST_BUCKET,
            Key=TEST_KEY)

    print(resp2)
    print()
    return resp, resp2


def aioboto_test():
    print('aioboto_test')
    loop = asyncio.get_event_loop()
    session = aiobotocore.session.get_session()

    async def go():
        async with session.create_client('s3', region_name=QUERY_REGION) as client:
            resp = await client.put_object(
                    Bucket=TEST_BUCKET,
                    Key=TEST_KEY,
                    Body=b'hello')

            print(resp)
            print()

            resp2 = await client.get_object(
                    Bucket=TEST_BUCKET,
                    Key=TEST_KEY)

            print(resp2)
            print()

        return resp, resp2

    loop.run_until_complete(go())

create_client.create_bucket(Bucket=TEST_BUCKET,
                          CreateBucketConfiguration={'LocationConstraint': CREATE_REGION})

try:
    boto_test()
    aioboto_test()
finally:
    create_client.delete_object(Bucket=TEST_BUCKET, Key=TEST_KEY)
    create_client.delete_bucket(Bucket=TEST_BUCKET)

