
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder
from resource import Resource

class UserGroup(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table('user_group_rels')

    def create(self, params):
        if params.get('is_admin'):
            params["is_admin"] = True
        else:
            params["is_admin"] = False
        return Resource.create(self, params)
        """try:
            response = self.table.put_item(
               Item=params
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("PutItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))"""

    def delete(self, params):
        try:
            response = self.table.delete_item(
                Key={
                    'user_id': params['user_id'],
                    'group_id': params['group_id'],
                },
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("DeleteItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def find_by_group_ids(self, group_ids):
        eav = {}
        fe = 'group_id in ('
        for index, group_id in enumerate(group_ids):
            group_id_name = ':group_id_%s' % index
            if index == 0:
                fe += group_id_name
            else:
                fe += ', ' + group_id_name
            eav[group_id_name] = group_id
        fe += ')'
        print(fe)
        print(eav)
        return self.table.scan(
            FilterExpression=fe,
            ExpressionAttributeValues=eav
        )['Items']

    def find(self, params):

        if not params:
            return self.table.scan()['Items']

        if params.get('user_id') and params.get('group_id'):
            response = self.table.get_item(
                Key={
                    'user_id': params['user_id'],
                    'group_id': params['group_id'],
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
            fe = Key('user_id').eq(params['user_id']);
            response = self.table.scan(
                FilterExpression=fe,
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return response['Items']

        if params.get('group_id'):
            fe = Key('group_id').eq(params['group_id']);
            response = self.table.scan(
                FilterExpression=fe,
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return response['Items']

        if params.get('email'):
            from user import User
            user = User(self.dynamodb)
            user_items = user.find({'email': params['email']})
            if len(user_items) == 0:    return []
            fe = Key('user_id').eq(user_items[0]['id']);
            response = self.table.scan(
                FilterExpression=fe,
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return response['Items']

        return []
