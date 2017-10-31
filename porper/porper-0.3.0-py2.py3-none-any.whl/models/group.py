
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder
from resource import Resource

import uuid

class Group(Resource):

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = dynamodb.Table('groups')

    def create(self, params):
        if not params.get('id'):
            params['id'] = str(uuid.uuid4())
        return Resource.create(self, params)

    """def _find_by_ids(self, ids):
        eav = {}
        fe = 'id in ('
        for index, id in enumerate(ids):
            id_name = ':id_%s' % index
            if index == 0:
                fe += id_name
            else:
                fe += ', ' + id_name
            eav[id_name] = id
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
            return self._find_by_ids(params['ids'])

        return []"""
