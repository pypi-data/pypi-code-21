import os
import boto3
import logging
import traceback
from typing import List

from boto3.dynamodb.conditions import Key, Attr
from amaasinfra.authorization.token_utils import TokenAttribute, unpack_token

class AMaaSUser(object):

    __cache_clients = {}
    __environment = os.environ.get('AWS_ENV', 'dev').lower()


    @classmethod
    def create_clients(cls):
        if not cls.__cache_clients:
            region = os.environ.get('AWS_DEFAULT_REGION') or 'ap-southeast-1'
            dynamodb = boto3.resource('dynamodb', region_name=region)
            for table in  ['book_permissions', 'relationships']:
                table_name = cls.get_table_name(table)
                cls.__cache_clients[table_name] = dynamodb.Table(table_name)


    @classmethod
    def get_table_name(cls, table):
        return '_'.join([table, cls.__environment])


    def __init__(self, token: str, logger=None) -> None:
        attributes = unpack_token(token)
        user_amid = attributes.get(TokenAttribute.asset_manager_id.value)
        self.asset_manager_id = int(user_amid) if user_amid else None
        self.username = attributes.get(TokenAttribute.username.value)
        self.email = attributes.get(TokenAttribute.email.value)
        self.firstname = attributes.get(TokenAttribute.first_name.value, '')
        self.lastname = attributes.get(TokenAttribute.last_name.value, '')
        # amid 0-9 are reserved for system users
        self.system_user = self.asset_manager_id < 10 if self.asset_manager_id else False
        self.relationships: List[dict] = []
        self.data_sources: List[int] = []
        self.asset_manager_permissions: List[int] = []
        self.book_permissions: List[dict] = []
        self.logger = logger or logging.getLogger()
        self.create_clients()


    def load_relationships(self) -> 'AMaaSUser':
        if self.asset_manager_id is None:
            return self

        results = self._dynamo_query('relationships',
                                     Select='SPECIFIC_ATTRIBUTES',
                                     IndexName='related_id_index',
                                     ProjectionExpression='asset_manager_id,related_id,relationship_type,relationship_status',
                                     KeyConditionExpression=Key('related_id').eq(self.asset_manager_id),
                                     FilterExpression=Attr('relationship_status').eq('Active'))
        self.relationships = results
        return self


    def load_data_sources(self) -> 'AMaaSUser':
        if self.asset_manager_id is None:
            return self

        if not self.relationships:
            self.load_relationships()

        asset_manager_ids = [rel.get('asset_manager_id') for rel in self.relationships]
        data_providers = set()
        for asset_manager_id in asset_manager_ids:
            results = self._dynamo_query('relationships',
                                         Select='SPECIFIC_ATTRIBUTES',
                                         ProjectionExpression='related_id',
                                         KeyConditionExpression=Key('asset_manager_id').eq(asset_manager_id),
                                         FilterExpression=Attr('relationship_status').eq('Active') & Attr('relationship_type').eq('Data Provider'))
            data_providers |= {rel.get('related_id') for rel in results}
        self.data_sources = list(data_providers)
        return self

    def load_asset_manager_permissions(self) -> 'AMaaSUser':
        if self.asset_manager_id is None:
            return self

        if not self.relationships:
            self.load_relationships()

        if not self.data_sources:
            self.load_data_sources()

        permissions = {0, self.asset_manager_id}
        permissions |= {rel.get('asset_manager_id') for rel in self.relationships}
        permissions |= {data_source for data_source in self.data_sources}
        self.asset_manager_permissions = list(permissions)

        return self

    def get_relationship(self, kind='Employee') -> list:
        # {'related_id': Decimal('594'), 'relationship_status': 'Active', 'asset_manager_id': Decimal('593'), 'relationship_type': 'Employee'}
        return [ int(r['asset_manager_id']) for r in self.relationships if r['relationship_status'] == 'Active' and r['relationship_type'] == kind]

    def load_book_permissions(self) -> 'AMaaSUser':
        if self.asset_manager_id is None:
            return self

        def make_writable(entry):
            entry['permission'] = 'write'
            return entry

        results = self._dynamo_query('book_permissions',
                                     Select='SPECIFIC_ATTRIBUTES',
                                     IndexName='user_id_index',
                                     ProjectionExpression='asset_manager_id,book_id,#permission',
                                     KeyConditionExpression=Key('user_asset_manager_id').eq(self.asset_manager_id),
                                     ExpressionAttributeNames={"#permission": "permission"})


        # Looking in cache to avoid dependency on books (?)
        for amid in self.get_relationship("Administrator"):
            admin_result =  self._dynamo_query('book_permissions',
                                               Select='SPECIFIC_ATTRIBUTES',
                                               IndexName='asset_manager_id-index',
                                               ProjectionExpression='asset_manager_id,book_id,#permission',
                                               KeyConditionExpression=Key('asset_manager_id').eq(amid),
                                               ExpressionAttributeNames={"#permission": "permission"})
            results += list( map( make_writable, admin_result))

        # Now collate, in case we are admin in one company, and puny user in another
        # {'book_id': 'KDL_F_COUNTERBOOK', 'asset_manager_id': Decimal('592'), 'permission': 'write'}
        seen = dict()

        for a_book in results:
            key = "{}/{}".format(a_book['asset_manager_id'], a_book['book_id'])
            if key in seen.keys():
                if a_book['permission'] == 'write':
                    seen[key]['permission'] = 'write'
            else:
                seen[key] = a_book

        self.book_permissions = seen.values()
        return self



    def check_asset_manager_permissions(self, asset_manager_id_claims: List[int]) -> (bool, List[int]):
        """
        Returns the asset_manager_ids that the user does not have access to
        """
        error_asset_manager_ids = [int(asset_manager_id) for asset_manager_id in asset_manager_id_claims
                                   if int(asset_manager_id) not in self.asset_manager_permissions]
        return error_asset_manager_ids


    def check_book_permissions(self, asset_manager_id: int, book_id: str, permission: str) -> None:
        if not self.is_book_accessible(asset_manager_id, book_id, permission):
            raise ValueError('User %s does not have requested %s access to the book: %s' \
                             % (self.asset_manager_id, permission, book_id))

    def is_book_accessible(self, asset_manager_id: int, book_id: str, permission: str) -> bool:
        if self.system_user:
            return True

        if isinstance(asset_manager_id, str):
            asset_manager_id = int(asset_manager_id)

        if not self.book_permissions:
            self.load_book_permissions()

        if not self.relationships:
            self.load_relationships()

        # if user is an admin of the asset manager, he should have write permissions
        is_admin = next((rel for rel in self.relationships
                         if rel.get('asset_manager_id') == asset_manager_id
                         and rel.get('relationship_type') == 'Administrator'), None)

        if not is_admin:
            for perm in self.book_permissions:
                if (perm.get('book_id') == book_id or perm.get(book_id) == '*') and \
                                perm.get('asset_manager_id') == asset_manager_id:
                    if permission == 'write' and perm.get('permission') == 'read':
                        raise ValueError('User %s does not have requested %s access to the book: %s' \
                                         % (self.asset_manager_id, permission, book_id))
                    return True
            return False

        # All good
        return True


    def _dynamo_query(self, table, **kwargs):
        table_name = self.get_table_name(table)
        cache = self.__cache_clients[table_name]
        kwargs['TableName'] = table_name
        return cache.query(**kwargs).get('Items',[])
