#!/usr/bin/env python
# -*- coding: utf-8 -*-
from yosaipy2.core import account_abcs
from pymongo import MongoClient
from yosaipy2.core.utils.utils import get_logger
from yosaipy2.account_store import models
from typing import List, Dict, Optional
from yosaipy2.core.conf.yosaisettings import LazySettings


class AccountStore(account_abcs.CredentialsAccountStore,
                   account_abcs.AuthorizationAccountStore,
                   account_abcs.LockingAccountStore):
    """
        AccountStore provides the realm-facing API to the relational database
        step 1:  generate an orm query
        step 2:  execute the query
        step 3:  return results
        """

    def __init__(self, settings):
        # type: (LazySettings) -> None
        """
        :param settings: lazy settings from yosai
        """
        settings = settings.ACCOUNT_STORE
        self._settings = settings
        self._uri = settings['uri']
        self._dbname = settings['dbname']
        self._retry_limit = settings['retry_limit']
        self._client = MongoClient(self._uri)
        self._db = self._client[self._dbname]
        self._logger = get_logger()

    def get_authc_info(self, identifier):
        """
        If an Account requires credentials from multiple data stores, this
        AccountStore is responsible for aggregating them (composite) and returning
        the results in a single account object.

        :returns: a dict of account attributes
        """
        user = self._retry_executor(self._query_user, None, identifier)
        if user is None:
            self._logger.error("user not found for specified id", extra={
                "identifier": identifier,
            })
            raise Exception("user not found")

        credentials = self._retry_executor(self._query_credential, [], identifier)
        if (credentials is None) or len(credentials) <= 0:
            self._logger.error("credential for user not found", extra={
                "identifier": identifier,
            })
            raise Exception("credential not found")

        authc_info = {c.credential_type: {'credential': c.credential, 'failed_attemps': []} for c in credentials}

        if 'totp_key' in authc_info:
            authc_info['totp_key']['2fa_info'] = {'phone_number': user.phone_number}

        return {
            'account_locked': user.account_lock_millis,
            'authc_info': authc_info
        }

    def get_authz_permissions(self, identifier):
        return self._retry_executor(self._query_permissions, {}, identifier)

    def get_authz_roles(self, identifier):
        roles = self._retry_executor(self._query_roles, [], identifier)
        return [r['name'] for r in roles]

    def lock_account(self, identifier, locked_time):
        table = self._db[models.User.table()]
        kwargs = {
            "filter": {"_id": identifier},
            "update": {"$set": {"account_lock_millis": locked_time}},
            "upsert": False
        }
        self._retry_executor(table.update_one, None, **kwargs)

    def unlock_account(self, identifier):
        return self.lock_account(identifier, 0)

    def _query_roles(self, identifier):
        user = self._query_user(identifier)
        if user is None:
            return []
        table = self._db[models.Role.table()]
        return list(table.find({'_id': {'$in': user.role_ids}}))

    def _query_permissions(self, identifier):
        # type:(str) -> Dict
        roles = self._query_roles(identifier)
        pids = []
        [pids.extend(r['permission_ids']) for r in roles]
        table = self._db[models.Permission.table()]
        result = dict()
        for p in table.find({'_id': {'$in': pids}}):
            domain = p['domain']
            if domain not in result:
                result[domain] = []
            detail = {
                'domain': [p['domain']],
                'actions': p['actions'] if 'actions' in p else ['*'],
                'targets': p['targets'] if 'targets' in p else ['*']
            }
            result[domain].append(detail)
        return result

    def _query_user(self, identifier):
        # type: (str) -> Optional[models.User]
        table = self._db[models.User.table()]
        user = table.find_one({'_id': identifier})
        if user is None:
            return None
        return models.User(user['_id'], **user)

    def _query_credential(self, identifier):
        # type: (str) -> List[models.Credential]
        table = self._db[models.Credential.table()]
        creds = list(table.find({'user_id': identifier}))
        return [models.Credential(c['_id'], **c) for c in creds]

    def _retry_executor(self, f, default, *args, **kwargs):
        counter = 0
        while counter < self._retry_limit:
            try:
                return f(*args, **kwargs)
            except Exception as exp:
                counter += 1
                self._logger.error("execute mongo query failed", extra={
                    "reason": exp,
                    "func_args": args,
                    "func_kwargs": kwargs,
                    "counter": counter,
                    "limit": self._retry_limit
                })
                if counter >= self._retry_limit:
                    raise
        return default
