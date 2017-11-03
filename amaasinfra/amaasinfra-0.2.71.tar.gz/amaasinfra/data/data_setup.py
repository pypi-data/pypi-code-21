import click
import os
import pymysql
from configparser import ConfigParser, NoSectionError
from amaasinfra.config.amaas_config import AMaaSConfig

class DatabaseSetter(object):
    def __init__(self):
        pass

    def recreate(self, schema, environment, db_config={}):
        environment = environment.lower()
        config = AMaaSConfig()
        if environment in ['dev', 'staging']:
            click.echo(f"Using {environment} Settings")
            server = config.get_config_value(environment, 'db_server')
            username = config.get_config_value(environment, 'db_username')
            password = config.get_config_value(environment, 'db_password')
        elif environment == 'automation':
            click.echo(f"Using automation Settings")
            server = db_config.get('db_server')
            username = db_config.get('db_username')
            password = db_config.get('db_password')
        else:
            click.echo("Using Local Settings")
            server = "localhost"
            username = "root"
            password = "amaas"
        #connect to the server and create database
        try:
            click.echo("Connecting to the server")
            conn = pymysql.connect(server, user=username, passwd=password, charset='utf8')
            conn.cursor().execute("SET time_zone = '+00:00';")
            click.echo("Creating schema: " + schema)
            conn.cursor().execute("DROP DATABASE IF EXISTS "+ schema +";")
            conn.cursor().execute("CREATE DATABASE "+schema+" CHARACTER SET utf8 COLLATE utf8_unicode_ci;")
            conn.cursor().execute("USE "+schema+";")
            click.echo("Schema " + schema + " created successfully.")
        except (pymysql.InternalError, pymysql.OperationalError):
            raise Exception('Error Creating DB and Connection')

        automated = True if environment == 'automation' else False

        if not automated:
            tables_path = os.path.join(os.getcwd() + "/tables")
            data_path = os.path.join(os.getcwd() + "/data")
        else:
            tables_path = db_config.get('table_path')
            data_path = db_config.get('data_path')

        files = [(f, tables_path) for f in os.listdir(tables_path)]
        if os.path.exists(data_path):
            files += [(f, data_path) for f in os.listdir(data_path)]
        # Execute sql files
        try:
            for file, path in files:
                if automated and file in db_config.get('ignore'):
                    continue
                file_path = os.path.join(path, file)
                with open(file_path) as sql_file:
                    click.echo("Reading: " + file_path)
                    content = sql_file.readlines()
                exe_line = ''
                for line in content:
                    exe_line += line.partition('#')[0].rstrip()
                    if exe_line != '' and str(exe_line[-1]) == ';':
                        click.echo("Executing: " + exe_line)
                        conn.cursor().execute(exe_line)
                        exe_line = ''
                click.echo("Ran SQL: " + file[:-4] + " successfully")
            conn.commit()
        except pymysql.OperationalError:
            raise Exception('Error executing mysql files in tables')
