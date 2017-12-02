from boto3.dynamodb.conditions import Key
from dynamodb_meta_store.exceptions import TableNotReadyException, \
    MisconfiguredSchemaException, ItemNotFound
import logging
import boto3
import decimal

log = logging.getLogger(__name__)


class DynamoDBMetaStore(object):
    """ DynamoDB Config Store instance """

    def __init__(
            self, aws_region, table_name, store_name,
            store_key='_store', option_key='_option',
            read_units=1, write_units=1):
        """ Constructor for the config store
        :type aws_region: str
        :param aws_region: AWS region to use
        :type table_name: str
        :param table_name: Name of the DynamoDB table to use
        :type store_name: str
        :param store_name: Name of the DynamoDB Config Store
        :type store_key: str
        :param store_key: Key name for the store in DynamoDB. Default _store
        :type option_key: str
        :param option_key: Key name for the option in DynamoDB. Default _option
        :returns: None
        """
        self.connection = boto3.resource('dynamodb', aws_region)
        self.table_name = table_name
        self.store_name = store_name
        self.store_key = store_key
        self.option_key = option_key
        self.read_units = read_units
        self.write_units = write_units
        self._initialize_table()

    def _initialize_table(self):
        """ Initialize the table
        :returns: None
        """
        try:
            self.table = self.connection.Table(self.table_name)
            status = self.table.table_status
            schema = self.table.key_schema

            # Validate that the table is in ACTIVE state
            if status not in ['ACTIVE', 'UPDATING']:
                raise TableNotReadyException

            # Validate schema
            hash_found = False
            range_found = False
            for key in schema:
                if key['AttributeName'] == self.store_key:
                    if key['KeyType'] == 'HASH':
                        hash_found = True

                if key['AttributeName'] == self.option_key:
                    if key['KeyType'] == 'RANGE':
                        range_found = True

            if not hash_found or not range_found:
                raise MisconfiguredSchemaException

        except self.connection.meta.client.exceptions.ResourceNotFoundException:
            self.table = self._create_table()

        self.table.reload()

    def _create_table(self):
        """ Create a new table
        :returns: dynamodb.Table -- return DynamoDB Table instance
        """
        table = self.connection.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': self.store_key,
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': self.option_key,
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': self.store_key,
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': self.option_key,
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': self.read_units,
                'WriteCapacityUnits': self.write_units
            }
        )

        table.wait_until_exists()

        return table

    def reload(self):
        """ Reload the config store
        :returns: None
        """
        self._initialize_store()

    def set(self, option, item):
        """ Upsert a config item
        A write towards DynamoDB will be executed when this method is called.
        :type option: str
        :param option: Name of the configuration option
        :type item: dict
        :param item: Dictionary with all option data
        :returns: bool -- True if the data was stored successfully
        """
        item[self.store_key] = self.store_name
        item[self.option_key] = option

        response = self.table.put_item(Item=item)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def get(self, option=None, keys=None):
        """ Get a config item
        A query towards DynamoDB will always be executed when this
        method is called.
        An boto.dynamodb2.exceptions.ItemNotFound will be thrown if the config
        option does not exist.
        :type option: str
        :param option: Name of the configuration option, all options if None
        :type keys: list
        :param keys: List of keys to return (used to get subsets of keys)
        :returns: dict -- Dictionary with all data; {'key': 'value'}
        """
        if option:
            items = self.get_option(option=option, keys=keys)
            return replace_decimals(items)
        else:
            items = {}
            partition_filter = {'key': self.store_key, 'value': self.store_name}
            response_items = self.query(partition_filter=partition_filter)
            for item in response_items:
                option = item[self.option_key]

                # Remove metadata
                del item[self.store_key]
                del item[self.option_key]

                items[option] = {k: v for k, v in item.items()}

            return replace_decimals(items)

    def get_option(self, option, keys=None):
        """ Get a specific option from the store.
        A query towards DynamoDB will always be executed when this
        method is called.
        get_option('a') == get(option='a')
        get_option('a', keys=['b', 'c']) == get(option='a', keys=['b', 'c'])
        :type option: str
        :param option: Name of the configuration option
        :type keys: list
        :param keys: List of keys to return (used to get subsets of keys)
        :returns: dict -- Dictionary with all data; {'key': 'value'}
        """

        response = self.table.get_item(
            Key={
                self.store_key: self.store_name,
                self.option_key: option
            },
        )
        try:
            item = response['Item']
        except KeyError:
            raise ItemNotFound("Item %s not found" % self.store_name)

        del item[self.store_key]
        del item[self.option_key]

        if keys:
            return {
                key: value
                for key, value in item.items()
                if key in keys
            }
        else:
            return {key: value for key, value in item.items()}

    def query(
        self, partition_filter, total_items=None, start_key=None
    ):
        """
        Query for an item with or without using global secondary index
        PARAMS:
        @table_name: name of the table
        @sort_key: Dict containing key and val of sort key
        e.g. {'name': 'uuid', 'value': '077f4450-96ee-4ba8-8faa-831f6350a860'}
        @partition_key: Dict containing key and val of partition key
        e.g. {'name': 'date', 'value': '2017-02-12'}
        @index_name (optional): Name of the Global Secondary Index
        """

        pk = partition_filter['key']
        pkv = partition_filter['value']
        if not start_key:
            response = self.table.query(
                KeyConditionExpression=Key(pk).eq(pkv)
            )
        else:
            response = self.table.query(
                KeyConditionExpression=Key(pk).eq(pkv),
                ExclusiveStartKey=start_key
            )
        if not total_items:
            total_items = response['Items']
        else:
            total_items.extend(response['Items'])
        if response.get('LastEvaluatedKey'):
            start_key = response['LastEvaluatedKey']
            return_items = self.query_item(
                partition_key=partition_filter, total_items=total_items,
                start_key=start_key
            )
            return return_items
        else:
            return total_items

    def __del__(self):
        self.connection.meta.client._endpoint.http_session.close()  # closing a boto3 resource


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = replace_decimals(v)
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj