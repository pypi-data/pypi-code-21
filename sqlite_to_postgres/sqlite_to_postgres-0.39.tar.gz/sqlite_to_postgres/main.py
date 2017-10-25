#!/usr/bin/env python3

import argparse
import configparser
import logging
import os
import subprocess

def setup_logging(args, task_uuid):
    logging.basicConfig(
        filename=os.path.join(task_uuid + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logger = logging.getLogger(__name__)
    return logger

def write_pgpass(conn_dict,logger):
    logger.info('write_pgpass()')
    pgpass_string = conn_dict['hostname'] + ':' + conn_dict['port'] + ':' + conn_dict['database'] + ':' + conn_dict['username'] + \
                     ':' + conn_dict['password']
    pgpass_path = '.pgpass'
    if os.path.exists(pgpass_path):
        os.remove(pgpass_path)
    with open(pgpass_path, 'w') as f_open:
        f_open.write(pgpass_string)
    os.chmod(pgpass_path, 0o400)
    logger.info('~write_pgpass()')
    return pgpass_path

def get_connect_dict(config_path, ini_section):
    config = configparser.ConfigParser()
    config.read(config_path)
    connect_dict = dict(config[ini_section])
    return connect_dict

def allow_create_fail(sql_path, logger):
    shell_cmd = "sed '/PRAGMA/d' " + sql_path + " > pragma_free.sql"
    output = subprocess.check_output(shell_cmd, shell=True)
    shell_cmd = "sed 's/CREATE TABLE/CREATE TABLE IF NOT EXISTS/g' pragma_free.sql > create_table.sql"
    output = subprocess.check_output(shell_cmd, shell=True)
    shell_cmd = "sed '/CREATE INDEX/d' create_table.sql > " + sql_path
    output = subprocess.check_output(shell_cmd, shell=True)
    return

def main():
    parser = argparse.ArgumentParser('write sqlite file to postgres')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('--source_sqlite_path', required=True)
    parser.add_argument('--postgres_creds_path', required=False)
    parser.add_argument('--ini_section', required=True)
    parser.add_argument('--task_uuid', required=True)
    args = parser.parse_args()

    ini_section = args.ini_section
    postgres_creds_path = args.postgres_creds_path
    source_sqlite_path = args.source_sqlite_path
    task_uuid = args.task_uuid
    
    logger = setup_logging(args, task_uuid)

    source_sqlite_name, source_sqlite_ext = os.path.splitext(os.path.basename(source_sqlite_path))
    logger.info('source_sqlite_name = %s' % source_sqlite_name)

    #dump
    source_dump_name = source_sqlite_name + '.sql'
    cmd = ['sqlite3', source_sqlite_path, "\'.dump\'", '>', source_dump_name ]
    shell_cmd = ' '.join(cmd)
    output = subprocess.check_output(shell_cmd, shell=True)

    #alter text create table/index
    allow_create_fail(source_dump_name, logger)

    #get postgres creds
    postgres_creds_path = args.postgres_creds_path
    kwargs = {'config_path': postgres_creds_path,
              'ini_section': ini_section}
    conn_dict = get_connect_dict(**kwargs)
    pgpass_path = write_pgpass(conn_dict,logger)

    #load
    cmd = ['psql', '-f', source_dump_name, '-U', conn_dict['username'], '-w', '-d', conn_dict['database'], '-h', conn_dict['hostname']]
    env = dict()
    env.update(os.environ)
    env['PGPASSFILE'] = pgpass_path
    output = subprocess.check_output(cmd, env=env, stderr=subprocess.STDOUT)
    os.remove(pgpass_path)
    return

if __name__ == '__main__':
    main()
