# coding: utf-8
#
# Copyright 2017 Kirill Vercetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import os

from pony.orm import Database

from .loader import Loader


class DatabaseFacade(object):
    """PonyORM Database object Facade"""

    def __init__(self, module_with_entities, **config):
        self.__config = config

        self.__set_module(module_with_entities)
        self.__init_defaults()

    def __init_defaults(self):
        """Initializes the default connection settings."""

        self.__config.setdefault('type', 'sqlite')

        db_type = self.__config.get('type')

        if db_type == 'sqlite':
            self.__config.setdefault('dbname', ':memory:')
        elif db_type == 'mysql':
            self.__config.setdefault('port', 3306)
        elif db_type == 'postgres':
            self.__config.setdefault('port', 5432)
        elif db_type == 'oracle':
            self.__config.setdefault('port', 1521)

        self.__config.setdefault('host', 'localhost')
        self.__config.setdefault('user', None)
        self.__config.setdefault('password', None)
        self.__config.setdefault('dbname', None)
        self.__config.setdefault('charset', 'utf8')

    def __set_module(self, mod):
        if not inspect.ismodule(mod):
            mod = Loader().load_and_registry(mod)

        db = getattr(mod, 'db')

        if not isinstance(db, Database):
            raise RuntimeError('The db module variable must be a Database object')

        self.__module = mod
        self.__db = db

    def bind(self):
        config = self.__config
        db_type = config.get('type')
        args = [db_type]
        kwargs = {}

        if db_type == 'sqlite':
            filename = config.get('dbname')

            if filename != ':memory:' and not os.path.dirname(filename):
                filename = os.path.join(os.getcwd(), filename)

            kwargs.update({
                'filename': filename,
                'create_db': True
            })
        elif db_type == 'mysql':
            kwargs.update({
                'host': config.get('host'),
                'port': config.get('port'),
                'user': config.get('user'),
                'passwd': config.get('password'),
                'db': config.get('dbname'),
                'charset': config.get('charset')
            })
        elif db_type == 'postgres':
            kwargs.update({
                'host': config.get('host'),
                'port': config.get('port'),
                'user': config.get('user'),
                'password': config.get('password'),
                'database': config.get('dbname')
            })
        elif db_type == 'oracle':
            args.append('{user}/{password}@{host}:{port}/{dbname}'.format(user=config.get('user'),
                                                                          password=config.get('password'),
                                                                          host=config.get('host'),
                                                                          port=config.get('port'),
                                                                          dbname=config.get('dbname')
                                                                          ))

        self.db.bind(*args, **kwargs)

    def connect(self):
        self.bind()
        self.db.generate_mapping(create_tables=True)

    @property
    def db(self):
        return self.__db
