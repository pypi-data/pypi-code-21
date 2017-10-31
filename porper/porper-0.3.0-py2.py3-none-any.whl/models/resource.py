
from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal_encoder import DecimalEncoder

class Resource:

    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table = None

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
            return params

    def update(self, params):
        if params.get('id') is None:
            raise Exception("no id is given in update")
        ue = ""
        eav = {}
        ean = {}
        for key in params.keys():
            if key == 'id': continue
            if ue != "":
                ue += ', '
            ue += "#%s = :%s" % (key, key)
            eav[':%s' % key] = params[key]
            ean['#%s' % key] = key
        ue = "set " + ue
        print(ue)
        print(eav)
        print(ean)
        try:
            response = self.table.update_item(
                Key={
                    'id': params["id"]
                },
                UpdateExpression=ue,
                ExpressionAttributeValues=eav,
                ExpressionAttributeNames=ean,
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise
        else:
            print("UpdateItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def find_by_id(self, id):
        response = self.table.get_item(
            Key={
                'id': id
            }
        )
        if response.get('Item'):
            item = response['Item']
            print("GetItem succeeded:")
            print(json.dumps(item, indent=4, cls=DecimalEncoder))
            return item
        else:
            print("GetItem returns no item:")
            return None

    def add_filter_with_multiple_values(self, fe, ean, eav, key, values):
        if fe != "":
            fe += " and "
        fe += '#%s in (' % key
        for index, val in enumerate(values):
            val_name = ':%s_%s' % (key, index)
            if index == 0:
                fe += val_name
            else:
                fe += ', ' + val_name
            eav[val_name] = val
        ean['#%s' % key] = key
        fe += ')'
        return fe

    def build_filters(self, params, fe, ean, eav, exceptions):
        for key in params.keys():
            if not params[key]: continue
            if key in exceptions:   continue
            if isinstance(params[key], list):
                key_single = key[:len(key)-1]    # truncate 's'
                fe = self.add_filter_with_multiple_values(fe, ean, eav, key_single, params[key])
            else:
                if fe != "":
                    fe += " and "
                fe += "#%s = :%s" % (key, key)
                #print(fe)
                eav[':%s' % key] = params[key]
                ean['#%s' % key] = key
        return fe

    def find_by_ids(self, ids):
        ean = {}
        eav = {}
        fe = ""
        """fe = 'id in ('
        for index, id in enumerate(ids):
            id_name = ':id_%s' % index
            if index == 0:
                fe += id_name
            else:
                fe += ', ' + id_name
            eav[id_name] = id
        fe += ')'"""
        fe += self.add_filter_with_multiple_values(fe, ean, eav, "id", ids)

        print(fe)
        print(eav)
        return self.table.scan(
            FilterExpression=fe,
            ExpressionAttributeNames=ean,
            ExpressionAttributeValues=eav
        )['Items']

    def find(self, params):

        print('resource find params : %s' % params)

        if not params:
            return self.table.scan()['Items']

        num_keys = len(params.keys())
        if num_keys == 1:
            if params.get('id'):
                item = self.find_by_id(params['id'])
                if not item: return []
                else:   return [item]
            if params.get('ids'):
                return self.find_by_ids(params['ids'])

        fe = ""
        ean = {}
        eav = {}
        for key in params.keys():
            if not params[key]: continue
            if isinstance(params[key], list):
                key_single = key[:len(key)-1]    # truncate 's'
                fe = self.add_filter_with_multiple_values(fe, ean, eav, key_single, params[key])
            else:
                if fe != "":
                    fe += " and "
                fe += "#%s = :%s" % (key, key)
                eav[':%s' % key] = params[key]
                ean['#%s' % key] = key

        # append 'ids' filter
        """if params.get('ids'):
            if fe != "":
                fe += " and "
            fe += '#id in ('
            for index, id in enumerate(params['ids']):
                id_name = ':id_%s' % index
                if index == 0:
                    fe += id_name
                else:
                    fe += ', ' + id_name
                eav[id_name] = id
            ean['#id'] = 'id'
            fe += ')'"""

        print(fe)
        print(ean)
        print(eav)

        print(self.table)
        response = self.table.scan(
            FilterExpression=fe,
            ExpressionAttributeNames=ean,
            ExpressionAttributeValues=eav
        )
        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))
        return response["Items"]

    def delete(self, id):
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
