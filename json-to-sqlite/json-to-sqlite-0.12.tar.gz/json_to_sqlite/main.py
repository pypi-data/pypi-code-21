#!/usr/bin/env python

import argparse
import datetime
import json
import logging
import os
import time

import sqlalchemy
import pandas as pd

def setup_logging(args, uuid):
    logging.basicConfig(
        filename=os.path.join(uuid + '.log'),
        level=logging.INFO,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('convert json to column based sqlite')

    parser.add_argument('--input_json',
                        required=True
    )
    parser.add_argument('--task_uuid',
                        required=True
    )
    parser.add_argument('--table_name',
                        required=True
    )

    args = parser.parse_args()
    input_json = args.input_json
    task_uuid = args.task_uuid
    table_name = args.table_name

    logger = setup_logging(args, task_uuid)

    sqlite_name = task_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    time_seconds = time.time()
    datetime_now = str(datetime.datetime.now())

    data = json.loads(input_json)
    
    data['datetime_now'] = datetime_now
    data['time_seconds'] = [time_seconds]

    df = pd.DataFrame(data)
    df.to_sql(table_name, engine, if_exists='append')
    return

if __name__ == '__main__':
    main()
