#!/usr/bin/env python

import argparse
import json
import logging
import os
import sys

import pandas as pd
import sqlalchemy

def readgroup_to_db(json_data, task_uuid, engine, logger):
    table_name = 'readgroups'
    for rg_key in sorted(json_data.keys()):
        rg_dict = dict()
        rg_dict['task_uuid'] = [task_uuid]
        rg_dict['ID'] = json_data['ID']
        rg_dict['key'] = rg_key
        rg_dict['value'] = json_data[rg_key]
        df = pd.DataFrame(rg_dict)
        df.to_sql(table_name, engine, if_exists='append')
    return


def setup_logging(args, task_uuid):
    logging.basicConfig(
        filename=os.path.join(task_uuid + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


def main():
    parser = argparse.ArgumentParser('readgroup json db insertion')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)
    
    # Required flags.
    parser.add_argument('--json_path',
                        required = True
    )
    parser.add_argument('--task_uuid',
                        required = True
    )

    # setup required parameters
    args = parser.parse_args()
    task_uuid = args.task_uuid
    json_path = args.json_path

    logger = setup_logging(args, task_uuid)

    sqlite_name = task_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    with open(json_path, 'r') as json_open:
        json_data = json.load(json_open)
        readgroup_to_db(json_data, task_uuid, engine, logger)
        
    return

if __name__ == '__main__':
    main()
