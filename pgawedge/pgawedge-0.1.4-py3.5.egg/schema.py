# from abc import ABC
#
# from postpy import base as pg
# from sqlalchemy import DDL, event
#
# from pgawedge import declare_schema, drop_schema
#
#
# def mount_declare_schema(target_schema):
#
#     schema = pg.Schema(target_schema.schema)
#     ddl_statement = DDL(schema.create_statement())
#     event.listen(target_schema, 'before_create',
#                  ddl_statement.execute_if(dialect='postgresql'))
#
#     return target_schema
#
#
# class AlchemySchema(ABC):
#
#     schema_name = ''
#     meta_schema = None
#     default_data_map = dict()
#
#     def __init__(self):
#         mount_declare_schema(self.meta_schema)
#
#     def declare(self, engine):
#         """Declare schemas and tables and seed any initial records."""
#
#         # declare_schema(engine, self.schema_name)
#
#         with engine.begin() as conn:
#             with conn.begin_nested():
#                 self.create(conn)
#                 self.seed_data(conn)
#
#     def reset(self, engine):
#         """Drop associated tables, rebuild them."""
#
#         with engine.begin() as conn:
#             with conn.begin_nested():
#                 self.drop(conn)
#                 # TODO see if can use declare here
#                 self.create(conn)
#                 self.seed_data(conn)
#
#     def create(self, conn):
#         self.meta_schema.create_all(conn)
#
#     def drop(self, conn):
#         """Remove the schema and data."""
#
#         # maybe? https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/testing/util.py
#
#         self.meta_schema.drop_all(conn)
#
#     def teardown(self, engine):
#         """Completely removes schema namespace."""
#
#         self.drop(engine)
#         drop_schema(engine, self.schema_name)
#
#     def seed_data(self, conn):
#         """Insert default/seed data."""
#
#         data_map = self.get_seed_data_map()
#
#         with conn.begin():
#             for table in self.meta_schema.sorted_tables:
#                 if table.name in data_map:
#                     # delete data and reinsert
#                     conn.execute(table.delete())
#                     conn.execute(table.insert(data_map[table.name]))
#
#     def get_seed_data_map(self):
#         return self.default_data_map
