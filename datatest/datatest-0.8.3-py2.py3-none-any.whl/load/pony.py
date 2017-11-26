# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .csvreader import UnicodeCsvReader


def csv_as_pony(file, encoding='utf-8', **kwds_types):
    import pony.orm

    with UnicodeCsvReader(file, encoding) as reader:
        columns = next(reader)  # Header row.

        # Set unique name for primary key.
        pk = 'id'
        while pk in columns:
            pk = '_' + pk

        # Define other columns.
        cls_dict = {}
        cls_dict[pk] = pony.orm.PrimaryKey(int, auto=True)
        for column in columns:
            cls_dict[column] = pony.orm.Optional(str)

        # Set type-overrides.
        for col_name, col_type in kwds_types.items():
            cls_dict[col_name] = pony.orm.Optional(col_type)

        # Create Pony ORM Entity and bind to SQLite database.
        db = pony.orm.Database()
        PonyEntity = pony.orm.core.EntityMeta('PonyEntity', (db.Entity,), cls_dict)
        db.bind('sqlite', ':memory:')
        db.generate_mapping(create_tables=True)

        with pony.orm.db_session:
            for row in reader:
                dict_row = dict(zip(columns, row))
                PonyEntity(**dict_row)  # <- Insert record.

        return PonyEntity
