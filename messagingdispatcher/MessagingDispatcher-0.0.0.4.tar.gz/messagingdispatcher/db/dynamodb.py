import json, os, sys
from boto3 import resource
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
from messagingdispatcher.db.basedb import BaseDB
import config

class DynamoDB(BaseDB):
    def __init__(self, table_name, allowed_type):
        self._dynamodb_resource = resource('dynamodb')
        self._table = self._dynamodb_resource.Table(table_name)
        self._allowed_type = allowed_type

    def add(self, item):
        if isinstance(item, self._allowed_type):
            return self._table.put_item(Item=item.to_dict())
        else:
            raise TypeError('Invalid argument. {} object is expected'.format(self._allowed_type))

    def add_batch(self, items):
        if isinstance(items, list):
            new_list = list(filter(lambda item: isinstance(item, self._allowed_type), items))
            if len(items) != len(new_list):
                raise TypeError('Invalid argument. {} object is expected for all list elements'.format(self._allowed_type))
            else:
                new_list = []
                for item in items:
                    new_list.append({'PutRequest': {'Item':item.to_dict()}})

                try:
                    if self._dynamodb_resource.batch_write_item(RequestItems={self._table.name: new_list}).get('UnprocessedItems'):
                        raise RuntimeError('Unable to process the batch insertion process.')
                    else:
                        return True
                except ClientError as error:
                    raise error
        else:
            raise TypeError('Invalid argument. List object is expected')

    def get(self, key, value):
        try:
            return self._table.get_item(Key={key: value}).get('Item', None)
        except ClientError as error:
            raise error

    def get_all(self, filter_key=None, filter_value=None, partial_match=False):
        """
        Perform a scan operation on table.
        Can specify filter_key (col name) and its value to be filtered.
        """

        if filter_key and filter_value:
            filtering_exp = Key(filter_key).eq(filter_value) if not partial_match else Key(filter_key).begins_with(filter_value)
            response = self._table.scan(FilterExpression=filtering_exp)
        else:
            response = self._table.scan()

        return response.get('Items', [])

    def update(self, key, value, update_key, update_value):
        # to prevent it from creating new item if key-value pair not found.
        # it should be handled by add function
        try:
            if self.get(key, value):
                return self._table.update_item(Key={key: value},
                                               UpdateExpression="SET {} = :updated".format(update_key),
                                               ExpressionAttributeValues={':updated': update_value},
                                               ReturnValues='UPDATED_NEW').get('Attributes', None)
            else:
                raise KeyError('No key-value pair found.')
        except ClientError as error:
            raise error

    def delete(self, key, value):
        try:
            if self.get(key, value):
                self._table.delete_item(Key={key: value})
                return True
            else:
                raise KeyError('No key-value pair found and deleted')
        except ClientError as error:
            raise error

    def purge(self):
        try:
            items = self._table.scan().get('Items', [])

            for item in items:
                self._table.delete_item(Key={list(item.keys())[0]: list(item.values())[0]})
        except Exception as e:
            raise e
