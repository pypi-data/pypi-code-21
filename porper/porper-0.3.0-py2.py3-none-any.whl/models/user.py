
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder
from resource import Resource

class User(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table('users')

    """def create(self, params):
        try:
            response = self.table.put_item(
               Item=params
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("PutItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
            return params['id']

    def _find_by_ids(self, items):
        eav = {}
        fe = 'id in ('
        for index, item in enumerate(items):
            id_name = ':id_%s' % index
            if index == 0:
                fe += id_name
            else:
                fe += ', ' + id_name
            eav[id_name] = item['user_id']
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

        if params.get('group_id'):
            from user_group import UserGroup
            user_group = UserGroup(self.dynamodb)
            user_group_items = user_group.find({'group_id': params['group_id']})
            if len(user_group_items) == 0: return []
            items = self._find_by_ids(user_group_items)
            if len(items) == 0: return []
            for user_group_item in user_group_items:
                user_item = [user_item for user_item in items if user_item['id'] == user_group_item['user_id']][0]
                for key in user_item.keys():
                    user_group_item[key] = user_item[key]
            for i in user_group_items:
                print(json.dumps(i, cls=DecimalEncoder))
            return user_group_items

        if params.get('group_ids'):
            from user_group import UserGroup
            user_group = UserGroup(self.dynamodb)
            user_group_items = user_group._find_by_group_ids(params['group_ids'])
            #print(user_group_items)
            if len(user_group_items) == 0: return []
            items = self._find_by_ids(user_group_items)
            if len(items) == 0: return []
            for user_group_item in user_group_items:
                user_item = [user_item for user_item in items if user_item['id'] == user_group_item['user_id']][0]
                for key in user_item.keys():
                    user_group_item[key] = user_item[key]
            for i in user_group_items:
                print(json.dumps(i, cls=DecimalEncoder))
            return user_group_items

        if params.get('id'):
            response = self.table.get_item(
                Key={
                    'id': params['id']
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

        if params.get('ids'):
            eav = {}
            fe = 'id in ('
            for index, id in enumerate(params['ids']):
                id_name = ':id_%s' % index
                if index == 0:
                    fe += id_name
                else:
                    fe += ', ' + id_name
                eav[id_name] = id
            fe += ')'
            print(fe)
            print(eav)
            response = self.table.scan(
                FilterExpression=fe,
                ExpressionAttributeValues=eav
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return response["Items"]

        if params.get('email'):
            response = self.table.scan(
                FilterExpression="email = :email",
                ExpressionAttributeValues={":email": params['email']}
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return response["Items"]

        return []"""
