
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder
from resource import Resource

import dateutil.parser

class AccessToken(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table('access_tokens')

    def create(self, params):
        params["time_stamp"] = dateutil.parser.parse(params['refreshed_time']).strftime("%s")   # will be used as TTL attribute
        """try:
            response = self.table.put_item(
               Item=params
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("PutItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
            return params['access_token']"""
        return Resource.create(self, params)

    def update(self, params):
        try:
            response = self.table.update_item(
                Key={
                    'access_token': params["access_token"]
                },
                UpdateExpression="set refresh_token = :rtoken, refreshed_time=:rtime, time_stamp=:ts",
                ExpressionAttributeValues={
                    ':rtoken': params['refresh_token'],
                    ':rtime': params['refreshed_time'],
                    ':ts': dateutil.parser.parse(params['refreshed_time']).strftime("%s")
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("UpdateItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def find(self, params):

        if not params:
            return self.table.scan()['Items']

        if params.get('access_token'):
            response = self.table.get_item(
                Key={
                    'access_token': params["access_token"]
                }
            )
            if response.get('Item'):
                item = response['Item']
                print("GetItem succeeded:")
                print(json.dumps(item, indent=4, cls=DecimalEncoder))
                return [item]
            else:
                print("GetItem returns no item:")
                return []

        if params.get('user_id'):
            return self.table.scan(
                FilterExpression="user_id = :user_id",
                ExpressionAttributeValues={":user_id": params['user_id']}
            )['Items']

        raise Exception("not permitted")
