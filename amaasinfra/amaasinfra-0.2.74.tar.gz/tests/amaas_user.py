"""
Crude tests.  Need a better way to mock out the DynamoDB calls
"""
import unittest
import uuid
import boto3
from moto import mock_dynamodb2
from mock import patch
import random
from amaasutils.random_utils import random_string
from amaasinfra.authorization.amaas_user import AMaaSUser
from amaasinfra.authorization.token_utils import TokenAttribute

class AMaaSUserTest(unittest.TestCase):
    def setUp(self):
        self.mock_dynamodb = mock_dynamodb2()
        self.mock_dynamodb.start()
        self.company_amid = random.randint(101, 150)
        self.user_amid = random.randint(151, 200)

        try:
            client = boto3.client('dynamodb')
            for table_name in ['relationships_dev', 'book_permissions_dev']:
                client.delete_table(TableName=table_name)
                waiter = client.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name)
        except:
            pass
        dynamodb = boto3.resource('dynamodb')
        dynamodb.create_table(
            TableName='relationships_dev',
            KeySchema=[
                {'AttributeName': 'asset_manager_id', 'KeyType': 'HASH'},
                {'AttributeName': 'relationship_id', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[
                {'AttributeName': 'asset_manager_id', 'AttributeType': 'N'},
                {'AttributeName': 'relationship_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
            {
                'IndexName': 'related_id_index',
                'KeySchema': [{'AttributeName': 'related_id', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5}}],
            ProvisionedThroughput={'ReadCapacityUnits': 5,
                                   'WriteCapacityUnits': 5})
        dynamodb.create_table(
            TableName='book_permissions_dev',
            KeySchema=[
                {'AttributeName': 'asset_manager_id', 'KeyType': 'HASH'},
                {'AttributeName': 'permission_id', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[
                {'AttributeName': 'asset_manager_id', 'AttributeType': 'N'},
                {'AttributeName': 'permission_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
            {
                'IndexName': 'user_id_index',
                'KeySchema': [{'AttributeName': 'user_asset_manager_id', 'KeyType': 'HASH'}],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5}}],
            ProvisionedThroughput={'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5})


    def insert_items(self, table_name: str, items: list) -> None:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        for item in items:
            table.put_item(Item=item)


    def tearDown(self):
        self.mock_dynamodb.stop()

    def setup_relationships(self):
        relationships = [{'asset_manager_id': self.company_amid,
                          'relationship_id': uuid.uuid4().hex,
                          'related_id': self.user_amid,
                          'relationship_status': 'Active',
                          'relationship_type': 'Employee'}]
        for data_provider in [10,11,12]:
            relationships.append({'asset_manager_id': self.company_amid,
                                  'relationship_id': uuid.uuid4().hex,
                                  'related_id': data_provider,
                                  'relationship_status': 'Active',
                                  'relationship_type': 'Data Provider'})
        self.insert_items('relationships_dev', relationships)

    @patch('amaasinfra.authorization.amaas_user.unpack_token')
    def testCheckAmidPermissions(self, mock_unpack_token):
        self.setup_relationships()
        mock_unpack_token.return_value = {TokenAttribute.asset_manager_id.value: self.user_amid}

        user = AMaaSUser('').load_asset_manager_permissions()
        errors = user.check_asset_manager_permissions([self.user_amid, self.company_amid, 10, 11, 12])
        self.assertFalse(errors)

        errors = user.check_asset_manager_permissions([self.company_amid])
        self.assertTrue(len(errors) == 0)

        errors = user.check_asset_manager_permissions([str(self.company_amid), 10])
        self.assertTrue(len(errors) == 0)

        errors = user.check_asset_manager_permissions([self.company_amid + 1])
        self.assertTrue(self.company_amid + 1 in errors)

        with self.assertRaises(ValueError):
            errors = user.check_asset_manager_permissions(['Invalid101'])


    @patch('amaasinfra.authorization.amaas_user.unpack_token')
    def testCheckNewUserPermissions(self, mock_unpack_token):
        mock_unpack_token.return_value = {TokenAttribute.username.value: 'new_user'}
        user = AMaaSUser('').load_asset_manager_permissions()

        claims = [10, 11, 12, 101]
        errors = user.check_asset_manager_permissions(claims)
        self.assertEqual(claims, errors)


    @patch('amaasinfra.authorization.amaas_user.unpack_token')
    def test_CheckBookPermissions(self, mock_unpack_token):
        self.setup_relationships()
        with_write_permissions = [self.generate_book_permission(company_amid=self.company_amid,
                                                                user_amid=self.user_amid,
                                                                permission='write')
                                  for _ in range(random.randint(1, 5))]
        with_read_permissions = [self.generate_book_permission(company_amid=self.company_amid,
                                                               user_amid=self.user_amid,
                                                               permission='read')
                                 for _ in range(random.randint(1, 5))]
        without_permissions = [self.generate_book_permission(company_amid=self.company_amid + 1,
                                                             user_amid=self.user_amid)
                               for _ in range(random.randint(1, 2))] + \
                              [self.generate_book_permission(company_amid=self.company_amid,
                                                             user_amid=self.user_amid + 1)
                               for _ in range(random.randint(1, 2))]
        permissions = with_read_permissions + with_write_permissions + without_permissions
        self.insert_items('book_permissions_dev', permissions)

        mock_unpack_token.return_value = {TokenAttribute.asset_manager_id.value: self.user_amid}
        user = AMaaSUser('').load_book_permissions()

        for permission in with_write_permissions:
            try:
                user.check_book_permissions(self.company_amid, permission.get('book_id'), 'write')
                user.check_book_permissions(self.company_amid, permission.get('book_id'), 'read')
            except:
                self.fail('Raised exception on permissioned book.')

        for permission in with_read_permissions:
            with self.assertRaises(ValueError):
                user.check_book_permissions(self.company_amid, permission.get('book_id'), 'write')
            try:
                user.check_book_permissions(self.company_amid, permission.get('book_id'), 'read')
            except:
                self.fail('Raised exception on permissioned book.')

        for permission in without_permissions:
            with self.assertRaises(ValueError):
                user.check_book_permissions(self.company_amid, permission.get('book_id'), 'write')
                user.check_book_permissions(self.company_amid, permission.get('book_id'), 'read')


    def generate_book_permission(self, company_amid=None, user_amid=None, permission=None):
        return {'asset_manager_id': company_amid or self.company_amid,
                'user_asset_manager_id': user_amid or self.user_amid,
                'permission_id': uuid.uuid4().hex,
                'book_id': random_string(6),
                'permission': permission or random.choice(['write', 'read']),
                'permission_status': 'Active'}


if __name__ == '__main__':
    unittest.main()
