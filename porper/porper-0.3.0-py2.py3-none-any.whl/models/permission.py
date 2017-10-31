
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder

class Permission:

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table('permissions')

    def _generate_id(self, params):
        id = ""
        if params.get('user_id'):
            id = 'u-%s' % params['user_id']
        elif params.get('group_id'):
            id = 'g-%s' % params['group_id']
        return '%s-%s-%s-%s' % (id, params.get('resource'), params.get('action'), params.get('value'))

    def create(self, params):
        params['id'] = self._generate_id(params)
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
            return params

    def _find_id(self, params):
        if params.get('user_id') is None and params.get('group_id') is None:
            return None
        fe = "action = :action and resource = :resource and #value = :value"
        ean = {'#value': 'value'}
        eav = {':action': params['action'], ':resource': params['resource'], ':value': params['value']}
        if params.get('user_id'):
            fe += " and user_id = :user_id"
            eav[':user_id'] = params['user_id']
        elif params.get('group_id'):
            fe += " and group_id = :group_id"
            eav[':group_id'] = params['group_id']
        response = self.table.scan(
            FilterExpression=fe,
            ExpressionAttributeNames=ean,
            ExpressionAttributeValues=eav
        )
        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))
        if len(response["Items"]) == 0: return None
        else:   return response["Items"][0]['id']

    def delete(self, params):
        id = params.get('id')
        if id is None:
            id = self._find_id(params)
        if id is None:
            print("No item found to delete")
            return None
        try:
            response = self.table.delete_item(
                Key={
                    'id': id
                },
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("DeleteItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
            return id

    def find(self, params):

        if not params:
            return self.table.scan()['Items']

        fe = ""
        ean = {}
        eav = {}
        if params.get('resource'):
            if fe != "":
                fe += " and "
            fe += "#resource = :resource"
            eav[':resource'] = params['resource']
            ean['#resource'] = 'resource'
        if params.get('action'):
            if fe != "":
                fe += " and "
            fe += "#action = :action"
            eav[':action'] = params['action']
            ean['#action'] = 'action'
        if params.get('value'):
            if fe != "":
                fe += " and "
            fe += "#value in (:value1, :value2)"
            eav[':value1'] = params['value']
            eav[':value2'] = '*'
            ean['#value'] = 'value'
        if params.get('user_id'):
            if params.get('all'):
                from user_group import UserGroup
                user_group = UserGroup(self.dynamodb)
                user_group_items = user_group.find({'user_id': params['user_id']})
                group_ids = [ user_group_item['group_id'] for user_group_item in user_group_items ]
                if fe != "":
                    fe += " and "
                if len(group_ids) == 0:
                    fe += "#user_id = :user_id"
                else:
                    fe += "(#user_id = :user_id or group_id in ("
                    for index, group_id in enumerate(group_ids):
                        group_id_name = ':group_id_%s' % index
                        if index == 0:
                            fe += group_id_name
                        else:
                            fe += ', ' + group_id_name
                        eav[group_id_name] = group_id
                    fe += '))'
                eav[':user_id'] = params['user_id']
                print(fe)
                print(eav)
            else:
                if fe != "":
                    fe += " and "
                fe += "#user_id = :user_id"
                eav[':user_id'] = params['user_id']
            ean['#user_id'] = 'user_id'
        elif params.get('group_id'):
            if fe != "":
                fe += " and "
            fe += "#group_id = :group_id"
            eav[':group_id'] = params['group_id']
            ean['#group_id'] = 'group_id'
        print(fe)
        print(ean)
        print(eav)
        response = self.table.scan(
            FilterExpression=fe,
            ExpressionAttributeNames=ean,
            ExpressionAttributeValues=eav
        )
        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))
        return response["Items"]
