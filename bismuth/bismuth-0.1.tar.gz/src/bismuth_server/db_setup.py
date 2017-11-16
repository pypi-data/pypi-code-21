# coding=utf-8
from os.path import dirname, join


async def create_schema(db_conn):
    with open(join(dirname(__file__), 'postgres', '1_schema_types.sql'), 'r', encoding='utf-8') as f:
        # These statements must be run line-by-line for postgres reasons.
        parts = list(f)
    with open(join(dirname(__file__), 'postgres', '2_schema.sql'), 'r', encoding='utf-8') as f:
        parts.append(f.read())
    for part in parts:
        if not part.startswith('--'):  # do not dispatch comments
            await db_conn.execute(part)
