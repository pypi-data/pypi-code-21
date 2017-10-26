#!/usr/bin/env python

import argparse
import logging
import os

import sqlalchemy
import pandas as pd

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

def get_ls_size(file_path):
    f_open = open(file_path,'r')
    line = f_open.readline().strip()
    f_open.close()
    line_split = line.split(' ')
    file_size = line_split[4]
    return file_size

def get_ls_filename(file_path):
    f_open = open(file_path,'r')
    line = f_open.readline().strip()
    f_open.close()
    line_split = line.split(' ')
    ls_path = line_split[-1]
    ls_name = os.path.basename(ls_path)
    return ls_name

def get_md5sum(file_path):
    f_open = open(file_path,'r')
    line = f_open.readline().strip()
    f_open.close()
    line_split = line.split(' ')
    md5sum = line_split[0]
    return md5sum

def get_sha256sum(file_path):
    f_open = open(file_path,'r')
    line = f_open.readline().strip()
    f_open.close()
    line_split = line.split(' ')
    sha256sum = line_split[0]
    return sha256sum

def main():
    parser = argparse.ArgumentParser('update status of job')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('--input_state',
                        required=True
    )
    parser.add_argument('--ls_l_path',
                        required=True
    )
    parser.add_argument('--md5sum_path',
                        required=True
    )
    parser.add_argument('--sha256sum_path',
                        required=True
    )
    parser.add_argument('--task_uuid',
                        required=True
    )

    args = parser.parse_args()

    ls_l_path = args.ls_l_path
    md5sum_path = args.md5sum_path
    sha256sum_path = args.sha256sum_path
    task_uuid = args.task_uuid
    input_state = args.input_state

    logger = setup_logging(args, task_uuid)

    sqlite_name = task_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    ls_size = get_ls_size(ls_l_path)
    ls_filename = get_ls_filename(ls_l_path)
    md5sum = get_md5sum(md5sum_path)
    sha256sum = get_sha256sum(sha256sum_path)

    integrity_dict = dict()
    integrity_dict['filename'] = ls_filename
    integrity_dict['input_state'] = input_state
    integrity_dict['md5sum'] = md5sum
    integrity_dict['sha256sum'] = sha256sum
    integrity_dict['size'] = ls_size
    integrity_dict['task_uuid'] = [task_uuid]

    table_name = 'integrity'
    df = pd.DataFrame(integrity_dict)
    df.to_sql(table_name, engine, if_exists='append')
    return

if __name__ == '__main__':
    main()
