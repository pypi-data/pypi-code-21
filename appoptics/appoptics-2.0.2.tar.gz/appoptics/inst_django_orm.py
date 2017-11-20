""" AppOptics instrumentation for Django ORM.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.
"""

from appoptics import util
import re

appoptics_logger = util.logger


def wrap_execute(func, f_args, f_kwargs, res):
    obj, sql = f_args[:2]
    kwargs = {}
    log_sql_args = not util.config.get('enable_sanitize_sql', True) and len(f_args) > 2
    if log_sql_args:
        kwargs['QueryArgs'] = str(f_args[2]).encode('utf-8')

    kwargs['Query'] = sql.encode('utf-8')
    if 'NAME' in obj.db.settings_dict:
        kwargs['Database'] = obj.db.settings_dict['NAME']
    if 'HOST' in obj.db.settings_dict:
        kwargs['RemoteHost'] = obj.db.settings_dict['HOST']
    if 'ENGINE' in obj.db.settings_dict:
        if re.search('post', obj.db.settings_dict['ENGINE']):
            kwargs['Flavor'] = 'postgresql'
        elif re.search('oracle', obj.db.settings_dict['ENGINE']):
            kwargs['Flavor'] = 'oracle'
    return kwargs


class CursorAppOpticsWrapper(object):
    ###########################################################################
    # Django cursors can be wrapped arbitrarily deeply with the following API.
    # Each class contains a references to the DB object, and the next level
    # cursor. Control passes to the cursor in execute and executemany, wrapped
    # with whatever behavior the wrapper provides.
    ###########################################################################

    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self):
        return iter(self.cursor)

    def execute(self, sql, params=()):
        return self.cursor.execute(sql, params)

    def executemany(self, sql, param_list):
        return self.cursor.executemany(sql, param_list)


def wrap(module):
    try:
        cursor_method = module.BaseDatabaseWrapper.cursor
        if getattr(cursor_method, '_appoptics_wrapped', False):
            return

        appoptics_wrapper = util.log_method(
            'djangoORM', callback=wrap_execute,
            store_backtrace=util._collect_backtraces('django_orm')
        )
        setattr(CursorAppOpticsWrapper, 'execute', appoptics_wrapper(CursorAppOpticsWrapper.execute))
        setattr(CursorAppOpticsWrapper, 'executemany', appoptics_wrapper(CursorAppOpticsWrapper.executemany))

        def cursor_wrap(self):
            try:
                return CursorAppOpticsWrapper(cursor_method(self), self)
            except Exception as e:
                appoptics_logger.debug("[AppOptics] Error in cursor_wrap: %s" % e)

        cursor_wrap._appoptics_wrapped = True

        setattr(module.BaseDatabaseWrapper, 'cursor', cursor_wrap)
    except Exception as e:
        appoptics_logger.error("[AppOptics] Error in module_wrap: %s" % e)
