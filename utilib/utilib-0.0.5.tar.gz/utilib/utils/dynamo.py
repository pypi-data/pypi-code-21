import boto3
import asyncio
import aioboto3

KeySchema = {
    'AttributeName': '',
    'KeyType': ''
}

AttributeDefinitions = {
    'AttributeName': '',
    'AttributeType': ''
}

ProvisionedThroughput = {
    'ReadCapacityUnits': 10,
    'WriteCapacityUnits': 10
}


class DynamoDBHelper:
    def __init__(self, key_id, access_key, region='cn-north-1'):
        self.aws_access_key_id = key_id
        self.aws_secret_access_key = access_key

        self.db = boto3.resource(
            'dynamodb',
            region_name=region,
            aws_access_key_id=key_id,
            aws_secret_access_key=access_key)

    def create_table(
            self,
            table_name,
            hash_key_name,
            hash_key_type,
            range_key_name=None,
            range_key_type=None,
            read_capacity_units=10,
            write_capacity_units=10):
        """
        创建dynamodb表(支持简单主键:hash_key和复合主键:hash_key&range_key)
        :param hash_key_name:Hash主键名称
        :param hash_key_type:Hash主键类型 Valid Values: S | N | B
                                S - the attribute is of type String
                                N - the attribute is of type Number
                                B - the attribute is of type Binary
        :param range_key_name:Range主键名称
        :param range_key_type:Range主键类型 Valid Values: S | N | B
        :param read_capacity_units:每秒需对此表执行的读取次数。
        :param write_capacity_units:每秒需对此表执行的写入次数
        :return:
        """
        key_schema = []
        attribute_definitions = []
        KeySchema['AttributeName'] = hash_key_name
        KeySchema['KeyType'] = 'HASH'
        AttributeDefinitions['AttributeName'] = hash_key_name
        AttributeDefinitions['AttributeType'] = hash_key_type
        attribute_definitions.append(AttributeDefinitions)
        key_schema.append(KeySchema)
        if range_key_name:
            KeySchema['AttributeName'] = range_key_name
            KeySchema['KeyType'] = 'RANGE'
            AttributeDefinitions['AttributeName'] = range_key_name
            AttributeDefinitions['AttributeType'] = range_key_type
            attribute_definitions.append(AttributeDefinitions)
            key_schema.append(KeySchema)
        ProvisionedThroughput['ReadCapacityUnits'] = read_capacity_units
        ProvisionedThroughput['WriteCapacityUnits'] = write_capacity_units
        self.db.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=ProvisionedThroughput
        )
        return True

    def del_table(self, table_name):
        self.db.meta.client.delete_table(TableName=table_name)
        return True

    def put_item(self, table_name, item):
        """
        插入单条数据
        :param item:必须包含主键，key与表对应，格式正确的json
        """
        table = self.db.Table(table_name)
        table.put_item(Item=item)
        return True

    def batch_write_item(self, table_name, items):
        """
        批量插入item
        """
        table = self.db.Table(table_name)
        while len(items) > 0:
            item_list = items[0:25]
            with table.batch_writer() as batch:
                for item in item_list:
                    batch.put_item(item)
            items = items[25:]
        return True

    def del_item(self, table_name, key):
        """
        删除数据
        :param key: 格式正确的json
        """
        table = self.db.Table(table_name)
        table.delete_item(Key=key)
        return True

    async def async_get_item(
            self,
            table_name,
            key,
            consistent_read=False):
        """
        使用项目的主键读取项目
         :type key: dict
         :param key: {
                        "hash_key":"key_name",
                        "range_key":"key_name"
                     }
        """
        async with aioboto3.resource(
                'dynamodb',
                region_name='cn-north-1',
                aws_secret_access_key=self.aws_secret_access_key,
                aws_access_key_id=self.aws_access_key_id
        ) as resource:
            table = resource.Table(table_name)
            response = await asyncio.get_event_loop().create_task(
                table.get_item(
                    Key=key,
                    ConsistentRead=consistent_read)
            )
        if 'Item' in response:
            item = response['Item']
            return item
        return None

    async def async_batch_get_item(self,
                                   table_name,
                                   keys,
                                   consistent_read=False):
        """
        批量获取item
        """
        requestItems = {}
        itemlist = []
        async with aioboto3.resource(
                'dynamodb',
                region_name='cn-north-1',
                aws_secret_access_key=self.aws_secret_access_key,
                aws_access_key_id=self.aws_access_key_id
        ) as resource:
            while len(keys) > 0:
                key_list = keys[0:100]
                requestItems[table_name] = {
                    'Keys': key_list
                }
                response = await asyncio.get_event_loop().create_task(
                    resource.meta.client.batch_get_item(
                        RequestItems=requestItems))
                itemlist.extend(response['Responses'][table_name])
                keys = keys[100:]
        return itemlist
