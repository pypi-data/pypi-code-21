
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder
from resource import Resource

class InvitedUser(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table('invited_users')
        self.INVITED = 'invited'
        self.REGISTERED = 'registered'

    """
    def create(self, params):
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
            return params['email']
    """

    def update(self, params):
        try:
            response = self.table.update_item(
                Key={
                    'email': params["email"],
                    'auth_type': params["auth_type"]
                },
                UpdateExpression="set #state = :state",
                ExpressionAttributeNames={
                    '#state': 'state'
                },
                ExpressionAttributeValues={
                    ':state': params['state']
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("UpdateItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def _fill_related_attrs(self, items):
        if len(items) == 0: return []
        from user import User
        user = User(self.dynamodb)
        user_items = user.find({'ids': [item['invited_by'] for item in items]})
        from group import Group
        group = Group(self.dynamodb)
        group_items = group.find({'ids': [item['group_id'] for item in items]})
        if len(user_items) == 0 or len(group_items) == 0:    return []
        for item in items:
            item['invited_by_email'] = [user_item['email'] for user_item in user_items if user_item['id'] == item['invited_by']][0]
            item['group_name'] = [group_item['name'] for group_item in group_items if group_item['id'] == item['group_id']][0]
        return items

    def find(self, params):
        """if params.get('email'):
            fe = "auth_type = :auth_type"
            eav = {":auth_type": params['auth_type']}
            if params['auth_type'] == 'slack':
                fe += " and slack_team_id = :slack_team_id and slack_bot_name = :slack_bot_name"
                eav[":slack_team_id"] = params['slack_team_id']
                eav[":slack_bot_name"] = params['slack_bot_name'].lower()
            items = self.table.query(
                KeyConditionExpression=Key('email').eq(params['email']),
                FilterExpression=fe,
                ExpressionAttributeValues=eav
            )
        else:
            items = Resource.find(self, params)
        if len(items) == 0: return []
        return self._fill_related_attrs(items)"""

        print(params)

        if params.get('email') and params.get('auth_type'):
            if len(params.keys()) > 2:
                fe = ""
                ean = {}
                eav = {}
                exceptions = ['email', 'auth_type']
                fe = self.build_filters(params, fe, ean, eav, exceptions)
                response = self.table.query(
                    KeyConditionExpression=Key('email').eq(params['email']) & Key('auth_type').eq(params['auth_type']),
                    FilterExpression=fe,
                    ExpressionAttributeNames=ean,
                    ExpressionAttributeValues=eav
                )
                for i in response['Items']:
                    print(json.dumps(i, cls=DecimalEncoder))
                return self._fill_related_attrs(response["Items"])
            else:
                response = self.table.get_item(
                    Key={
                        'email': params['email'],
                        'auth_type': params["auth_type"]
                    }
                )
                if response.get('Item'):
                    item = response['Item']
                    print("GetItem succeeded:")
                    print(json.dumps(item, indent=4, cls=DecimalEncoder))
                    return self._fill_related_attrs([item])
                else:
                    print("GetItem returns no item:")
                    return []

        items = Resource.find(self, params)
        if len(items) == 0: return []
        return self._fill_related_attrs(items)


        """if not params:
            return self.table.scan()['Items']

        if params.get('email'):
            response = self.table.get_item(
                Key={
                    'email': params['email']
                }
            )
            if response.get('Item'):
                item = response['Item']
                print("GetItem succeeded:")
                print(json.dumps(item, indent=4, cls=DecimalEncoder))
                return self._fill_related_attrs([item])
            else:
                print("GetItem returns no item:")
                return []

        if params.get('group_id'):
            response = self.table.scan(
                FilterExpression="group_id = :group_id",
                ExpressionAttributeValues={":group_id": params['group_id']}
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return self._fill_related_attrs(response["Items"])

        if params.get('group_ids'):
            eav = {}
            fe = 'group_id in ('
            for index, group_id in enumerate(params['group_ids']):
                group_id_name = ':group_id_%s' % index
                if index == 0:
                    fe += group_id_name
                else:
                    fe += ', ' + group_id_name
                eav[group_id_name] = group_id
            fe += ')'
            print(fe)
            print(eav)
            response = self.table.scan(
                FilterExpression=fe,
                ExpressionAttributeValues=eav
            )
            for i in response['Items']:
                print(json.dumps(i, cls=DecimalEncoder))
            return self._fill_related_attrs(response["Items"])

        return []"""
