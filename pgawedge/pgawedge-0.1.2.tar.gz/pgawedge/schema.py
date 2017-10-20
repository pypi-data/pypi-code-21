# from abc import ABC
#
# import sqlalchemy as sa
# from postpy.dml import compile_truncate_table
#
# from pgawedge import declare_schema, drop_schema, sa_meta_schema
#
#
# class AlchemySchema(ABC):
#     schema_name = None
#     meta_schema = sa_meta_schema(schema_name)
#     default_data_map = dict()
#
#     def declare(self, engine):
#         """Declare schemas and tables and insert any default data records."""
#
#         declare_schema(engine, self.schema_name)
#         self.meta_schema.create_all(engine)
#         self.store_default(engine)
#
#     def drop(self, engine):
#         """Remove the schema and data."""
#
#         self.meta_schema.drop_all(engine)
#
#     def reset(self, engine):
#         """Drop associated tables, rebuild them."""
#
#         self.drop(engine)
#         self.declare(engine)
#
#     def teardown(self, engine):
#         """Completely removes schema namespace."""
#
#         self.drop(engine)
#         drop_schema(engine, self.schema_name)
#
#     def store_default(self, engine):
#         """Insert initial records in any tables default data.
#
#         Notes
#         -----
#         Add data to tables requiring default/initialized data. Generally this
#         is for small mapping tables or tables with constant values.
#         """
#
#         with engine.begin() as conn:
#             for table in self.meta_schema.sorted_tables:
#                 if table.name in self.default_data_map:
#                     truncate_statement = compile_truncate_table(table.fullname)
#                     conn.execute(sa.text(truncate_statement))
#                     conn.execute(
#                         table.insert(self.default_data_map[table.name])
#                     )
