#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import codecs
import csv
import glob
import re
import yaml
import validictory
import odoorpc
from datetime import datetime, date as date_type
from dateutil import parser as dt_parser
import psycopg2

from dateutil.relativedelta import relativedelta
from odoorpc.tools import v
import ConfigParser
import click
from prettytable import PrettyTable
import os
import sys
import time
import random as pkg_random
import base64 as pkg_base64
import uuid as pkg_uuid
import string as pkg_string
import xlsxwriter
import code
import signal
from pprint import pprint
from os.path import expanduser
from lxml import etree
from dyools import IF, Operator, Logger

Log = Logger()

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

home = expanduser("~")
home = os.path.join(home, '.dyvz')

CONFIG_FILE = os.path.join(home, 'dyz.ini')

__VERSION__ = '0.6.1'

SCHEMA_GLOBAL = {
    "type": "object",
    "properties": {
        "repeat": {
            "type": "integer",
            "required": False,
            "minimum": 1,
        },
        "section": {
            "type": "string",
            "required": False,
        },
        "database": {
            "type": "string",
            "required": False,
        },
        "host": {
            "type": "string",
            "required": False,
        },
        "message": {
            "type": "object",
            "required": False,
            "properties": {
                "title": {
                    "type": "string",
                    "required": True,
                },
                "body": {
                    "type": "string",
                    "required": False,
                }
            },
        },
        "vars": {
            "required": False,
            "type": "array",
            "items": {
                "type": "object",
            },
        },
        "show": {
            "required": False,
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                },
                "fields": {
                    "type": "array",
                },
                "refs": {
                    "type": "any",
                    "required": False,
                },
                "order": {
                    "type": "string",
                    "required": False,
                },
                "limit": {
                    "type": "integer",
                    "required": False,
                },

            },
        },
        "import": {
            "required": False,
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                },
                "path": {
                    "type": "string",
                },
                "view_ref": {
                    "type": "string",
                    "required": False,
                },
                "map": {
                    "type": "object",
                    "items": {
                        "type": "object",
                    }
                },
                "keys": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "string",
                    }
                },
                "number": {
                    "type": "integer",
                    "required": False,
                },
                "random": {
                    "type": "boolean",
                    "required": False,
                },
                "pick": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "object",
                        "required": True,
                        "patternProperties": {
                            ".*": {
                                "type": ["array", "string"],
                            },
                        },
                    }
                },
            },
        },
        "record": {
            "type": "object",
            "required": False,
            "properties": {
                "model": {
                    "type": "string",

                },
                "refs": {
                    "type": "any",
                    "required": False,

                },
                "view_ref": {
                    "type": "string",
                    "required": False,

                },
                "key": {
                    "type": "string",
                    "required": False,
                },
                "order": {
                    "type": "string",
                    "required": False,

                },
                "limit": {
                    "type": "integer",
                    "required": False,
                },
                "values": {
                    "type": "array",
                    "required": False,

                },
                "show": {
                    "type": ["array", "boolean"],
                    "required": False,
                    "items": {
                        "type": "string",
                    },

                },
                "many2many": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "object",
                        "patternProperties": {
                            ".*": {
                                "type": 'string',
                                "enum": ['add', 'remove', 'replace']
                            }
                        }
                    },

                },
                "many2one": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "object",
                        "patternProperties": {
                            ".*": {
                                "type": 'array',
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "limit": {
                                            "type": "integer",
                                            "required": False,
                                        },
                                        "order": {
                                            "type": "string",
                                            "required": False,
                                        },
                                    }

                                }

                            }
                        }
                    },
                },
                "context": {
                    "type": "object",
                    "required": False,
                },
                "typology": {
                    "type": "string",
                    "required": False,
                    "enum": ['one', 'multi', 'last', 'model', 'first'],
                },

                "create": {
                    "type": "boolean",
                    "required": False,

                },
                "write": {
                    "type": "boolean",
                    "required": False,

                },
                "unlink": {
                    "type": "boolean",
                    "required": False,

                },
                "functions": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "object",
                        "required": False,
                        "properties": {
                            "name": {
                                "type": "string",
                            },
                            "args": {
                                "type": "object",
                                "required": False,
                            },
                            "api": {
                                "type": "string",
                                "required": False,
                                "enum": ['one', 'multi', 'model'],
                            },
                            "kwargs": {
                                "type": "boolean",
                                "required": False,
                            }
                        }
                    }
                },
                "workflows": {
                    "type": "array",
                    "required": False,

                },
                "export": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "object"
                    }

                },
                "pick": {
                    "type": "array",
                    "required": False,
                    "items": {
                        "type": "object",
                        "required": True,
                        "patternProperties": {
                            ".*": {
                                "type": ["array", "string"],
                            },
                        },
                    }

                },
            },
        }
    },
}


def error(_msg):
    click.secho(_msg, fg='red')
    click.secho('Aborted !', fg='red')
    sys.exit(-1)


def warn(_msg):
    click.secho(_msg, fg='yellow')


def validate(_data, _schema):
    try:
        validictory.validate(_data, _schema, disallow_unknown_properties=True)
    except Exception as e:
        error(e.message)


def generate_yaml_datas(N=20):
    def j(s, n=2):
        s = str(s)
        return s.rjust(n, '0')

    return {
        'today': [time.strftime(DATE_FORMAT)],
        'now': [time.strftime(DATETIME_FORMAT)],
        'product': [x for x in
                    "Mac;iMac;Iphone;MacBook;Phone;Speaker;Printer;Mouse;Keyboard;Disk;Machine;Mobile;Samsung S6;Paper x78;Screen 5';HeadPhones;Notepad;Pen;Rule;Cable RJ45".split(
                        ';')],
        'service': [x for x in "Installation;Maintenance;Configuration;Formation;Deployement".split(';')],
        'name': [x for x in
                 "Hildegard Follett;Antonina Kozak;Joette Tarver;Elvia Gorley;Earnest Tinner;Ada Steakley;Krystal Sheely;Percy Cairo;Earline Borchert;Sabrina Winberg;Mitzi Mires;Paola Slick;Monserrate Marra;Shana Chavarria;Jc Osuna;Emmitt Briones;Faviola Giannone;Carmelita Tejeda;Marietta Ragan;Marcelle Ruckman;Vada Galvan;Bobby Froelich;Annabel Brigman;Sanora Eley;Regan Kowalsky;Markita Griego;Mike Hanneman;Lakeshia Peden;Marth Cranston;Gustavo Tooley;Lisha Patt;Shanae Bruns;Jasper Veselka;Margurite Amoroso;Latesha Gumm;Glory Poirer;Efrain Marion;Marisha Alphin;Sebastian Mingle;Tiana Riel;Keeley Butner;Karoline Rehman;Lona Hanberry;Numbers Pflug;Liberty Murphey;Irving Berkowitz;Gwenn Westergard;Sherrell Wollard;Lizeth Francese;Nona Kocian".split(
                     ';')],
        'thisyear': [y + '-' + j(m) + '-' + j(d) for y, m, d in
                     ([time.strftime('%Y'), pkg_random.choice(range(1, 13)), pkg_random.choice(range(1, 29))] for g in
                      range(N))],
        'lastyear': [y + '-' + j(m) + '-' + j(d) for y, m, d in (
            [str(int(time.strftime('%Y')) - 1), pkg_random.choice(range(1, 13)), pkg_random.choice(range(1, 29))] for g
            in
            range(N))],
        'nextyear': [y + '-' + j(m) + '-' + j(d) for y, m, d in (
            [str(int(time.strftime('%Y')) + 1), pkg_random.choice(range(1, 13)), pkg_random.choice(range(1, 29))] for g
            in
            range(N))],
        'thismonth': [y + '-' + j(m) + '-' + j(d) for y, m, d in
                      ([time.strftime('%Y'), time.strftime('%m'), pkg_random.choice(range(1, 29))] for g in range(N))],
        'nextmonth': [y + '-' + j(m) + '-' + j(d) for y, m, d in
                      ([time.strftime('%Y'), str(int(time.strftime('%m')) + 1), pkg_random.choice(range(1, 29))] for g
                       in range(N))],
        'lastmonth': [y + '-' + j(m) + '-' + j(d) for y, m, d in
                      ([time.strftime('%Y'), str(int(time.strftime('%m')) - 1), pkg_random.choice(range(1, 29))] for g
                       in range(N))],
    }


yaml_datas = generate_yaml_datas()

try:
    os.makedirs(home)
except:
    pass

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w+') as config_file:
        pass


def raise_keyboard_interrupt(*a):
    raise KeyboardInterrupt()


class Console(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        try:
            import readline
            import rlcompleter
        except ImportError:
            print 'readline or rlcompleter not available, autocomplete disabled.'
        else:
            readline.set_completer(rlcompleter.Completer(locals).complete)
            readline.parse_and_bind("tab: complete")


class Shell(object):
    def init(self, args):
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)

    def console(self, local_vars):
        if not os.isatty(sys.stdin.fileno()):
            exec sys.stdin in local_vars
        else:
            Console(locals=local_vars).interact()


def process_domain(ctx, name, value):
    domain = []
    if value:
        for d in value:
            field, operator, value = d
            try:
                value = eval(value)
            except:
                pass
            operator = operator.replace('gte', '>=')
            operator = operator.replace('gt', '>')
            operator = operator.replace('lte', '<=')
            operator = operator.replace('lt', '<')
            operator = operator.replace('eq', '=')
            if operator.startswith('dt'):
                operator = operator[2:]
                value = parse_date_hash(ctx, value).strftime(DATETIME_FORMAT)
            if operator.startswith('d'):
                operator = operator[1:]
                value = parse_date_hash(ctx, value).strftime(DATE_FORMAT)
            domain.append((field, operator, value))
    return domain


def parse_date_hash(ctx, hash, dt=None):
    if not dt:
        dt = datetime.now()
    pattern = re.compile("([+-])*(\d+)([MSMHmdyw])")
    values = pattern.findall(hash)
    for sign, number, code in values:
        coeff = -1 if sign == '-' else 1
        number = int(number) if number and number.isdigit() else 0
        if not code:
            click.secho('the term %s is not processed' % hash, fg='red')
            ctx.abort()
        years = months = weeks = days = hours = minutes = seconds = microseconds = 0
        if code == 'M':
            microseconds = coeff * number
        if code == 'S':
            seconds = coeff * number
        if code == 'M':
            minutes = coeff * number
        if code == 'H':
            hours = coeff * number
        if code == 'd':
            days = coeff * number
        if code == 'm':
            months = coeff * number
        if code == 'y':
            years = coeff * number
        if code == 'w':
            weeks = coeff * number

        dt = dt + relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds
        )
    return dt


@click.group()
@click.option('--database', '-d', type=click.STRING, default='DEMO', help="The database")
@click.option('--host', '-h', type=click.STRING, default='localhost', help="The host of the server")
@click.option('--load', '-l', type=click.STRING, help="The name of section to load")
@click.option('--prompt-login', type=click.BOOL, is_flag=True, help="Prompt the Odoo parameters for loggin")
@click.option('--prompt-connect', type=click.BOOL, is_flag=True, help="Prompt the Odoo parameters for connection")
@click.option('--config', '-c',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True, readable=True,
                              resolve_path=True), default=CONFIG_FILE, help="The path of config")
@click.option('--export', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True,
                                          resolve_path=True))
@click.option('--port', '-p', type=click.INT, default=8069, help="The port of the server")
@click.option('--user', '-u', type=click.STRING, default='admin', help="The user of the database")
@click.option('--password', '-pass', type=click.STRING, default='admin', help="The password of the user")
@click.option('--superuserpassword', '-s', type=click.STRING, default='admin', help="The password of the super user")
@click.option('--protocol', type=click.Choice(['jsonrpc+ssl', 'jsonrpc']), default='jsonrpc', help="Protocol to use")
@click.option('--mode', '-m', type=click.Choice(['test', 'dev', 'prod']), default='dev', help="Database mode")
@click.option('--timeout', '-t', type=click.INT, default=60, help="Timeout in minutes")
@click.option('--yes', is_flag=True, default=False)
@click.option('--no-context', is_flag=True, default=False)
@click.version_option(__VERSION__, expose_value=False, is_eager=True, help="Show the version")
@click.pass_context
def cli(ctx, database, host, port, user, password, superuserpassword, protocol, timeout, config, load, mode, export,
        prompt_login, prompt_connect, yes, no_context):
    """CLI for Odoo"""
    odoo = False
    prompt_connect = prompt_login or prompt_connect

    def export_excel(data_to_export):
        if export:
            filename = 'EXPORT_%s.xlsx' % time.strftime('%Y%m%d_%H%M%S')
            export_file = os.path.join(export, filename)
            workbook = xlsxwriter.Workbook(export_file)
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': True})
            col, row = 0, 0
            for i, filename in enumerate(data_to_export._field_names):
                worksheet.write(row, col, str(data_to_export._field_names[i]), bold)
                col += 1
            for i, rowdata in enumerate(data_to_export._rows):
                row += 1
                col = 0
                for j, coldata in enumerate(data_to_export._rows[i]):
                    worksheet.write(row, col, str(coldata))
                    col += 1
            workbook.close()
            click.secho("The data is exported to %s" % export_file, fg='green')

    def echo(data_to_show):
        click.echo(data_to_show)
        export_excel(data_to_show)

    def secho(data_to_show, fg=None, bg=None):
        click.secho(data_to_show, fg=fg, bg=bg)
        export_excel(data_to_show)

    def xml_id(record, record_id=False):
        global odoo
        if not record:
            return ''
        if not record_id:
            res_model, res_id = record._name, record.id
        else:
            res_model, res_id = record, record_id
        IrModelData = odoo.env['ir.model.data']
        data_id = IrModelData.search([('model', '=', res_model), ('res_id', '=', res_id)])
        data = IrModelData.browse(data_id)
        return data.complete_name if data else ''

    def object_from_xml_id(xmlid):
        global odoo
        if not xmlid:
            return False
        xmlid_tuple = xmlid.strip().split('.')
        module = False
        if len(xmlid_tuple) == 2:
            module, xml_name = xmlid_tuple
        else:
            xml_name = xmlid
        IrModelData = odoo.env['ir.model.data']
        model_domain = [('name', '=', xml_name)]
        if module:
            model_domain.append(('module', '=', module))
        data_id = IrModelData.search(model_domain)
        data = IrModelData.browse(data_id)
        if data:
            return odoo.env[data.model].browse(data.res_id)
        return False

    def action_connect():
        global odoo
        if mode == 'prod':
            if not yes and not click.confirm('You are in mode production, continue ?'):
                sys.exit()
        try:
            click.secho('Try to connect to the host %s:%s, database=%s, mode=%s, timeout=%smin' % (
                host, port, database, mode, timeout / 60))
            odoo = odoorpc.ODOO(host, protocol=protocol, port=port, timeout=timeout)
            odoo.config['auto_context'] = not no_context
            click.secho('Connected to host %s:%s, database=%s, version=%s, mode=%s, timeout=%smin' % (
                host, port, database, odoo.version, mode, timeout / 60),
                        fg='green')
            ctx.obj['version'] = int(
                ''.join([x for x in odoo.version.strip() if x.isdigit() or x == '.']).split('.')[0])
        except:
            click.secho(
                'Cannot connect to host %s:%s, database=%s, mode=%s' % (host, port, database, mode),
                fg='red')
        return odoo

    def action_login():
        global odoo
        odoo = action_connect()
        if odoo:
            odoo = odoorpc.ODOO(host, protocol=protocol, port=port, timeout=timeout)
            try:
                click.secho('Try to login to the database %s as %s' % (database, user))
                odoo.login(database, user, password)
                click.secho('Connected to the database %s as %s' % (database, user), fg="green")
            except:
                click.secho('Cannot connect to the database %s as %s' % (database, user), fg="red")
        return odoo

    def update_list():
        global odoo
        if odoo:
            click.echo('Updating the list of modules ...')
            odoo.env['ir.module.module'].update_list()

    timeout *= 30

    config_obj = ConfigParser.ConfigParser()
    ctx.obj['config_obj'] = config_obj
    ctx.obj['config_path'] = config
    config_obj.read(config)
    if not load:
        for _sec in config_obj.sections():
            default = config_obj.has_option(_sec, 'default') and config_obj.getboolean(_sec, 'default') or False
            if default:
                load = _sec
    load_from_config = load and load in config_obj.sections()
    if load_from_config:
        click.secho('Loading data from the config file ...')
    ctx.obj['load'] = load
    ctx.obj['_database'] = database
    ctx.obj['_host'] = host
    ctx.obj['_port'] = port
    ctx.obj['_user'] = user
    ctx.obj['_password'] = password
    ctx.obj['_protocol'] = protocol
    ctx.obj['_superuserpassword'] = superuserpassword
    ctx.obj['_mode'] = mode
    ctx.obj['_default'] = False

    database = config_obj.get(load, 'database', database) if load_from_config else database
    host = config_obj.get(load, 'host', host) if load_from_config else host
    port = config_obj.getint(load, 'port') if load_from_config else port
    user = config_obj.get(load, 'user', user) if load_from_config else user
    password = config_obj.get(load, 'password', password) if load_from_config else password
    protocol = config_obj.get(load, 'protocol', protocol) if load_from_config else protocol
    mode = config_obj.get(load, 'mode', mode) if load_from_config else mode
    superuserpassword = config_obj.get(load, 'superuserpassword',
                                       superuserpassword) if load_from_config else superuserpassword
    if prompt_connect:
        host = click.prompt('host', host, type=str)
        port = click.prompt('port', default=port, type=str)
        superuserpassword = click.prompt('superuserpassword', default=superuserpassword, type=str)
        protocol = click.prompt('protocol', protocol, type=str)
    ctx.obj['prompt_database'] = False
    if prompt_login:
        ctx.obj['prompt_database'] = True
        database = click.prompt('database', default=database, type=str)
        user = click.prompt('user', default=user, type=str)
        password = click.prompt('password', default=password, type=str)
        mode = click.prompt('mode', default=mode, type=str)
    ctx.obj['database'] = database
    ctx.obj['host'] = host
    ctx.obj['port'] = port
    ctx.obj['user'] = user
    ctx.obj['password'] = password
    ctx.obj['protocol'] = protocol
    ctx.obj['superuserpassword'] = superuserpassword
    ctx.obj['mode'] = mode
    ctx.obj['odoo'] = odoo
    ctx.obj['action_login'] = action_login
    ctx.obj['action_connect'] = action_connect
    ctx.obj['odoo'] = odoo
    ctx.obj['xml_id'] = xml_id
    ctx.obj['object_from_xml_id'] = object_from_xml_id
    ctx.obj['echo'] = echo
    ctx.obj['secho'] = secho
    ctx.obj['update_list'] = update_list

    PROD_COMMANDS_BLACKLIST = [
        'db_drop',
        'db_restore',
        'db_create',
        'func',
        'module_install',
        'module_upgrade',
        'module_install_all',
        'module_uninstall',
        'install',
        'upgrade',
        'install_all',
        'uninstall',
        'truncate',
        'update_data',
        'load_yaml',
    ]
    if mode == 'prod' and ctx.invoked_subcommand in PROD_COMMANDS_BLACKLIST:
        click.secho('The command "%s" is not enabled in production mode !!' % ctx.invoked_subcommand)
        ctx.abort()


# database functions

@cli.command()
@click.pass_context
def pg_login(ctx):
    """Login to the postgresql"""
    echo = ctx.obj['echo']
    echo('Databases :')
    index = 0
    kw = {
        'host': ctx.obj['host'],
        'port': ctx.obj['port'],
        'user': ctx.obj['user'],
        'password': ctx.obj['password'],
    }
    databases = [ctx.obj['database']]
    if databases == ['all']:
        conn = psycopg2.connect(**kw)
        cur = conn.cursor()
        databses_sql = """
            SELECT datname FROM pg_database WHERE datistemplate = false;
        """
        cur.execute(databses_sql)
        databases = [x[0] for x in cur.fetchall()]
        conn.close()
    for db in databases:
        kw = dict(kw, database=db)
        conn = psycopg2.connect(**kw)
        cur = conn.cursor()
        table_sql = """
                SELECT count(*) 
                FROM pg_class
                WHERE relkind='r' 
                AND relname='res_users'
        """
        cur.execute(table_sql)
        count = cur.fetchone()[0]
        if count:
            index += 1
            echo(' %s -> %s' % (index, db,))
        conn.close()


@cli.command()
@click.pass_context
def pg_reset_passwords(ctx):
    """Reset password of given databases to admin"""
    echo = ctx.obj['echo']
    kw = {
        'host': ctx.obj['host'],
        'port': ctx.obj['port'],
        'user': ctx.obj['user'],
        'password': ctx.obj['password'],
    }
    databases = [ctx.obj['database']]
    if databases == ['all']:
        conn = psycopg2.connect(**kw)
        cur = conn.cursor()
        databses_sql = """
            SELECT datname FROM pg_database WHERE datistemplate = false;
        """
        cur.execute(databses_sql)
        databases = [x[0] for x in cur.fetchall()]
        conn.close()
    if not click.confirm('Continue on databases : %s' % databases):
        ctx.abort()
    for db in databases:
        echo('Switch to the database %s' % (db,))
        kw = dict(kw, database=db)
        conn = psycopg2.connect(**kw)
        cur = conn.cursor()
        table_sql = """
                SELECT count(*) 
                FROM pg_class
                WHERE relkind='r' 
                AND relname='res_users'
        """
        cur.execute(table_sql)
        count = cur.fetchone()[0]
        if count:
            cur = conn.cursor()
            update_sql = """
                            UPDATE res_users SET password='admin';
                            UPDATE res_users SET login='admin' where id=1;
            """
            cur.execute(update_sql)
            echo('Data are updated in the database %s' % (db,))
        if click.confirm('Commit ?'):
            conn.commit()
        cur.close()
        conn.close()


@cli.command()
@click.pass_context
@click.argument('tables', type=click.STRING, required=False, nargs=-1)
def pg_truncate(ctx, tables):
    """Truncate some postgresql tables"""
    if not tables:
        tables = [
            'mrp_production',
            'stock_picking',
            'stock_picking_wave',
            'stock_move',
            'stock_quant',
            'account_move',
            'account_move_line',
            'account_invoice',
            'account_payment',
            'account_bank_statement',
            'account_batch_deposit',
            'account_analytic_line',
            'sale_order',
            'sale_order_line',
            'purchase_order',
            'purchase_order_line',
            'procurement_order',
            'stock_inventory',
            'stock_scrap',
            'stock_production_lot',
            'stock_quant_package',
        ]
    echo = ctx.obj['echo']
    kw = {
        'host': ctx.obj['host'],
        'port': ctx.obj['port'],
        'user': ctx.obj['user'],
        'password': ctx.obj['password'],
    }
    databases = [ctx.obj['database']]
    if databases == ['all']:
        conn = psycopg2.connect(**kw)
        cur = conn.cursor()
        databses_sql = """
            SELECT datname FROM pg_database WHERE datistemplate = false;
        """
        cur.execute(databses_sql)
        databases = [x[0] for x in cur.fetchall()]
        conn.close()
    if not click.confirm('Continue to truncate tables %s on databases : %s' % (tables, databases)):
        ctx.abort()
    for db in databases:
        echo('Switch to the database %s' % (db,))
        kw = dict(kw, database=db)
        conn = psycopg2.connect(**kw)
        cur = conn.cursor()
        for table in tables:
            table_sql = """
                    SELECT count(*) 
                    FROM pg_class
                    WHERE relkind='r' 
                    AND relname=%s
            """
            cur.execute(table_sql, (table,))
            count = cur.fetchone()[0]
            if count:
                cur = conn.cursor()
                truncate_sql = """ TRUNCATE TABLE %s CASCADE """ % table
                cur.execute(truncate_sql)
                Log.success('The table <%s> is truncated in the database <%s>' % (table, db))
            else:
                Log.warn('The table <%s> not found in the database <%s>' % (table, db))
        if click.confirm('Commit ?'):
            conn.commit()
        cur.close()
        conn.close()


@cli.command()
@click.pass_context
def where(ctx):
    """Show actual informations"""
    echo = ctx.obj['echo']
    vars = ['host', 'port', 'database', 'user', 'password', 'superuserpassword', 'protocol', 'mode']
    x = PrettyTable()
    x.field_names = ["Key", "Value"]
    x.align["Key"] = x.align["Value"] = "l"
    kwargs = {}
    for var in vars:
        x.add_row([var.title(), ctx.obj.get(var, '')])
        kwargs[var] = ctx.obj.get(var, '')
    echo(x)
    echo('http://{host}:{port}/?db={database}   {user}/{password}'.format(**kwargs))
    echo('Section : {}'.format(ctx.obj['load']))


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.option('--fields', '-f', type=click.STRING, required=False, multiple=True)
@click.pass_context
def section_save(ctx, section, fields):
    """Save the config"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Save the config %s to %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        config.add_section(section)
    config.set(section, 'database', 'database' in fields and ctx.obj['_database'] or ctx.obj['database'])
    config.set(section, 'host', 'host' in fields and ctx.obj['_host'] or ctx.obj['host'])
    config.set(section, 'port', 'port' in fields and ctx.obj['_port'] or ctx.obj['port'])
    config.set(section, 'user', 'user' in fields and ctx.obj['_user'] or ctx.obj['user'])
    config.set(section, 'password', 'password' in fields and ctx.obj['_password'] or ctx.obj['password'])
    config.set(section, 'default', 'default' in fields and ctx.obj['_default'] or ctx.obj['default'])
    config.set(section, 'superuserpassword',
               'superuserpassword' in fields and ctx.obj['_superuserpassword'] or ctx.obj['superuserpassword'])
    config.set(section, 'protocol', 'protocol' in fields and ctx.obj['_protocol'] or ctx.obj['protocol'])
    config.set(section, 'mode', 'mode' in fields and ctx.obj['_mode'] or ctx.obj['mode'])
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)


def __section_create(ctx, section):
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Create new section %s to the config %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        config.add_section(section)
    else:
        click.secho('The section %s already exists' % section, fg='red')
        return
    host = click.prompt('host', default=ctx.obj['host'], type=str)
    port = click.prompt('port', default=ctx.obj['port'], type=str)
    database = click.prompt('database', default=ctx.obj['database'], type=str)
    user = click.prompt('user', default=ctx.obj['user'], type=str)
    password = click.prompt('password', default=ctx.obj['password'], type=str)
    superuserpassword = click.prompt('superuserpassword', default=ctx.obj['superuserpassword'], type=str)
    protocol = click.prompt('protocol', default=ctx.obj['protocol'], type=str)
    mode = click.prompt('mode', default=ctx.obj['mode'], type=str)
    config.set(section, 'host', host)
    config.set(section, 'port', port)
    config.set(section, 'database', database)
    config.set(section, 'user', user)
    config.set(section, 'password', password)
    config.set(section, 'superuserpassword', superuserpassword)
    config.set(section, 'protocol', protocol)
    config.set(section, 'mode', mode)
    config.set(section, 'default', True)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The section %s is created' % section, fg='green')


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def create(ctx, section):
    """Create a new section"""
    __section_create(ctx, section)


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_create(ctx, section):
    """Create a new section"""
    __section_create(ctx, section)


def __section_update(ctx, section):
    """Update a section"""
    if not section:
        section = ctx.obj['load']
    if not section:
        click.secho('Please specify a section', fg='red')
        ctx.abort()
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Update the section %s in the config %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        click.secho('The section %s does not found' % section, fg='red')
        return
    host = click.prompt('host', default=config.get(section, 'host'), type=str)
    port = click.prompt('port', default=config.get(section, 'port'), type=str)
    database = click.prompt('database', default=config.get(section, 'database'), type=str)
    user = click.prompt('user', default=config.get(section, 'user'), type=str)
    password = click.prompt('password', default=config.get(section, 'password'), type=str)
    superuserpassword = click.prompt('superuserpassword', default=config.get(section, 'superuserpassword'), type=str)
    protocol = click.prompt('protocol', default=config.get(section, 'protocol'), type=str)
    mode = click.prompt('mode', default=config.get(section, 'mode'), type=str)
    config.set(section, 'host', host)
    config.set(section, 'port', port)
    config.set(section, 'database', database)
    config.set(section, 'user', user)
    config.set(section, 'password', password)
    config.set(section, 'superuserpassword', superuserpassword)
    config.set(section, 'protocol', protocol)
    config.set(section, 'mode', mode)
    config.set(section, 'default', True)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The section %s is updated' % section, fg='green')


@cli.command()
@click.argument('section', type=click.STRING, required=False)
@click.pass_context
def update(ctx, section):
    """Update a section"""
    __section_update(ctx, section)


@cli.command()
@click.argument('section', type=click.STRING, required=False)
@click.pass_context
def section_update(ctx, section):
    """Update a section"""
    __section_update(ctx, section)


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def use(ctx, section):
    """Use a section"""
    __use_section(ctx, section)


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_use(ctx, section):
    """Use a section"""
    __use_section(ctx, section)


@cli.command()
@click.argument('section', type=click.STRING, required=True)
@click.pass_context
def section_set(ctx, section):
    """Set a section"""
    __use_section(ctx, section)


def __use_section(ctx, section):
    """Set a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Set the section %s in the config %s' % (section, config_path))
    config.read(config_path)
    if section not in config.sections():
        click.secho('The section %s does not found' % section, fg='red')
        return
    for _sec in config.sections():
        config.set(_sec, 'default', False)
    config.set(section, 'default', True)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The section %s is default' % section, fg='green')


@cli.command()
@click.pass_context
def section_unset(ctx):
    """Unset a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Unset the default section in the file %s' % config_path)
    config.read(config_path)
    for section in config.sections():
        config.set(section, 'default', False)
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)
    click.secho('The default section is unset', fg='green')


@cli.command()
@click.argument('section', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def section_delete(ctx, section):
    """Delete a section"""
    config = ctx.obj['config_obj']
    config_path = ctx.obj['config_path']
    click.echo('Delete sections %s from the config %s' % (section, config_path))
    config.read(config_path)
    for sec in section:
        if sec not in config.sections():
            click.secho('The section %s does not found' % sec, fg='red')
            continue
        else:
            config.remove_section(sec)
            click.secho('The section %s is removed' % sec, fg='green')
    with open(ctx.obj['config_path'], 'wb') as configfile:
        config.write(configfile)


@cli.command()
@click.pass_context
@click.argument('arg', type=click.STRING, required=False)
def section_list(ctx, arg):
    """Show section list"""
    __section_list(ctx, arg)


@cli.command()
@click.pass_context
@click.argument('arg', type=click.STRING, required=False)
def sections(ctx, arg):
    """Show section list"""
    __section_list(ctx, arg)


@cli.command()
@click.pass_context
@click.argument('arg', type=click.STRING, required=False)
def databases(ctx, arg):
    """Show section list"""
    __section_list(ctx, arg)


@cli.command()
@click.pass_context
@click.argument('arg', type=click.STRING, required=False)
def servers(ctx, arg):
    """Show section list"""
    __section_list(ctx, arg)


def __section_list(ctx, arg):
    """Show section list"""
    config = ctx.obj['config_obj']
    echo = ctx.obj['echo']
    config_path = ctx.obj['config_path']
    click.echo('List sections of the config')
    config.read(config_path)
    x = PrettyTable()
    if not arg:
        x.field_names = ["Section", "Database", "Host", "Port", "User", "Password", "Super User Password", "Protocol",
                         "Mode", "Default"]
    else:
        x.field_names = ["Section", "Database", arg.title()]
    for f in x.field_names:
        x.align[f] = 'l'
    for section in config.sections():
        if not arg:
            x.add_row([
                section,
                config.get(section, 'database', ''),
                config.get(section, 'host', ''),
                config.get(section, 'port', ''),
                config.get(section, 'user', ''),
                config.get(section, 'password', ''),
                config.get(section, 'superuserpassword', ''),
                config.get(section, 'protocol', ''),
                config.get(section, 'mode', ''),
                config.get(section, 'default', ''),
            ])
        else:
            x.add_row([
                section,
                config.get(section, 'database', ''),
                config.get(section, arg, ''),
            ])
    echo(x)


# Misc

@cli.command()
@click.argument('length', type=click.INT, default=24, required=False)
@click.option('--nbr', type=click.INT, default=1, required=False)
@click.option('--uuid', is_flag=True, type=click.BOOL, default=False, required=False)
@click.option('--base64', is_flag=True, type=click.BOOL, default=False, required=False)
@click.pass_context
def random(ctx, length, nbr, uuid, base64):
    """Generate random strings"""
    click.echo('Some random strings')
    echo = ctx.obj['echo']
    tab = []
    for i in range(nbr):
        if uuid:
            generated_string = str(pkg_uuid.uuid1())
        elif base64:
            generated_string = pkg_base64.b64encode(os.urandom(length))
        else:
            generated_string = ''.join(pkg_random.choice(pkg_string.letters + pkg_string.digits) for _ in range(length))
        tab.append(generated_string)
    x = PrettyTable()
    x.field_names = ["Random"]
    x.align["Random"] = "l"
    for r in tab:
        x.add_row([r])
    echo(x)


# Managing database

@cli.command()
@click.argument('output', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True,
                                          resolve_path=True), required=True)
@click.pass_context
def db_backup(ctx, output):
    """Backup the database"""
    database = ctx.obj['database']
    filename = '%s_%s.zip' % (database, time.strftime('%Y%m%d_%H%M%S'))
    path = os.path.join(output, filename)
    click.echo('Backup the database %s to %s' % (database, path))
    dump = ctx.obj['action_connect']().db.dump(ctx.obj['superuserpassword'], database)
    f = open(path, 'wb+')
    f.write(dump.getvalue())
    f.close()
    click.secho('The backup is stored to %s' % path, fg='green')


@cli.command()
@click.argument('input', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True,
                                         resolve_path=True), required=True)
@click.pass_context
def db_restore(ctx, input):
    """Restore a database"""
    database = ctx.obj['database']
    click.echo('Restore the database %s from %s' % (database, input))
    with open(input, 'rb') as backup_file:
        ctx.obj['action_connect']().db.restore(ctx.obj['superuserpassword'], database, backup_file)
    click.echo('The database is restored')


@cli.command()
@click.option('--yes', is_flag=True, default=False)
@click.pass_context
def db_drop(ctx, yes):
    """Drop the database"""
    database = ctx.obj['database']
    click.echo('Drop the database %s ' % database)
    if yes or click.confirm('Do you want to continue?'):
        ctx.obj['action_connect']().db.drop(ctx.obj['superuserpassword'], database)
        click.secho('The database is dropped', fg='green')
    else:
        click.secho('The database is not dropped', fg='red')


@cli.command()
@click.option('--yes', is_flag=True, default=False)
@click.pass_context
def db_create(ctx, yes):
    """Create a database"""
    ctx.obj['action_connect']()
    database = ctx.obj['database']
    if not ctx.obj['prompt_database']:
        database = click.prompt('Name of the database ?', database)
    click.echo('Create the database %s ' % database)
    demo = False
    lang = click.prompt('Language ?', 'fr_FR')
    if yes or click.confirm('Load demo data ?'):
        demo = True
    if yes or click.confirm('Do you want to continue?'):
        odoo.db.create(admin_password=ctx.obj['superuserpassword'], db=database, demo=demo, lang=lang,
                       password=ctx.obj['superuserpassword'])
        click.secho('The database is created', fg='green')
    else:
        click.secho('The database is not created', fg='red')


@cli.command()
@click.pass_context
def db_list(ctx):
    """List databases"""
    click.echo('List databases')
    odoo = ctx.obj['action_connect']()
    echo = ctx.obj['echo']
    x = PrettyTable()
    x.field_names = ["Name"]
    x.align["Name"] = "l"
    for db in odoo.db.list():
        x.add_row([db])
    echo(x)


# Access database

@cli.command()
@click.pass_context
def login(ctx):
    """Login to the database"""
    ctx.obj['action_login']()


@cli.command()
@click.pass_context
def shell(ctx):
    """Shell mode"""

    def records(model_name, args=None, limit=0, order='id asc'):
        model = odoo.env[model_name]
        if isinstance(args, (int, long)):
            return model.browse(args)
        elif hasattr(args, '__iter__'):
            if args:
                if isinstance(args[0], (int, long)):
                    return model.browse(args)
                else:
                    return model.browse(model.search(args, limit=limit, order=order))
        return model

    def model(model_name):
        return odoo.env[model_name]

    def read(model_name, domain=[], fields=[], limit=0):
        return odoo.env[model_name].search_read(domain, fields, limit=limit)

    def show(records, field='name'):
        if not isinstance(records, (list, tuple)):
            for rec in records:
                print "%s : %s" % (str(rec.id).rjust(3, ' '), getattr(rec, field, ''))
        else:
            for rec in records:
                print "%s : %s" % (str(rec.get('id')).rjust(3, ' '), rec.get(field, ''))

    get = records
    pp = pprint
    odoo = ctx.obj['action_login']()
    Shell().console(locals())


@cli.command()
@click.pass_context
def connect(ctx):
    """Connect to the server"""
    ctx.obj['action_connect']()


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--filter', '-f', type=click.STRING, required=False, multiple=True)
@click.option('--states', '-ss', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--store', '-s', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--depends', '-d', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--required', '-r', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--readonly', '-ro', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--domain', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--translate', '-t', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--relation', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--selection', type=click.BOOL, is_flag=True, required=False, default=False)
@click.option('--help', type=click.BOOL, is_flag=True, required=False, default=False)
@click.pass_context
def fields(ctx, model, filter, store, states, depends, required, readonly, domain, translate, relation, selection,
           help):
    """List fields of a model"""
    click.echo('Showing the fields of the model %s' % model)
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    Model = odoo.env[model]
    x = PrettyTable()
    # x.field_names = ["Name", "Type", "Label", "Relation/Selection", "Store", "Depends", "Required", "States"]
    header = ["Name", "Type", "Label"]
    if store:
        header.append('Store')
    if states:
        header.append('States')
    if depends:
        header.append('Depends')
    if required:
        header.append('Required')
    if readonly:
        header.append('Readonly')
    if domain:
        header.append('Domain')
    if translate:
        header.append('Translate')
    if relation:
        header.append('Relation')
    if selection:
        header.append('Selection')
    if help:
        header.append('Help')
    x.field_names = header

    x.align["Name"] = x.align["Type"] = x.align["Label"] = "l"
    # x.align["Name"] = x.align["Type"] = x.align["Label"] = x.align["Relation/Selection"] = x.align["States"] = "l"
    # x.align["Store"] = x.align["Depends"] = x.align["Required"] = "c"
    for key, value in Model.fields_get().iteritems():
        show = False
        if not filter:
            show = True
        elif value.get('type') in filter or key in filter or value.get('relation', False) in filter:
            show = True
        else:
            for f in filter:
                if f in value.get('type') or f in key or f in value.get('relation', ''):
                    show = True
        if show:
            relation_selection = value.get('relation', '')
            if not relation_selection and value.get('selection', ''):
                relation_selection = ','.join([tmp[0] for tmp in value.get('selection', '')])
            tab = [key, value.get('type', ''), value.get('string', '')]
            if store:
                tab.append(value.get('store', ''))
            if states:
                tab.append(value.get('states', ''))
            if depends:
                tab.append(','.join([tmp for tmp in value.get('depends', '')]))
            if required:
                tab.append(value.get('required', ''))
            if readonly:
                tab.append(value.get('readonly', ''))
            if domain:
                tab.append(value.get('domain', ''))
            if translate:
                tab.append(value.get('translate', ''))
            if relation:
                tab.append(value.get('relation', ''))
            if selection:
                tab.append(','.join([tmp[0] for tmp in value.get('selection', '')]))
            if help:
                tab.append(value.get('help', ''))
            x.add_row(tab)
            # x.add_row([key, value.get('type', ''), value.get('string', ''), relation_selection, value.get('store', ''),
            #            value.get('depends', ''), value.get('required', ''), value.get('states', '')])
    echo(x)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.argument('function', type=click.STRING, required=True)
@click.option('--id', default=False, type=click.STRING, required=False, multiple=True)
@click.option('--param', '-p', default=False, nargs=2, type=click.STRING, required=False, multiple=True)
@click.pass_context
def func(ctx, model, function, id, param):
    """Execute a function"""
    click.echo('Execute the function %s of the model %s' % (function, model))
    odoo = ctx.obj['action_login']()
    Model = odoo.env[model]
    if id:
        ids = [int(x) for x in id]
        Model = Model.browse(ids)
    args = {}
    for p_key, p_value in param:
        try:
            p_value = eval(p_value)
        except:
            pass
        args[p_key] = p_value
    click.echo('ids=%s, args=%s' % (id, args))
    click.echo(getattr(Model, function)(**args))


@cli.command()
@click.pass_context
def module_update_list(ctx):
    """Update list of modules"""
    ctx.obj['action_login']()
    ctx.obj['update_list']()
    click.secho('The list of module is updated', fg='green')


@cli.command()
@click.pass_context
def update_list(ctx):
    """Update list of modules"""
    ctx.obj['action_login']()
    ctx.obj['update_list']()
    click.secho('The list of module is updated', fg='green')


def __module_install(ctx, modules, module, update_list):
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    for module in Operator.unique([x.strip() for x in Operator.split_and_flat(',', modules, module)]):
        click.echo('Installing the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_immediate_install(module_id)
            click.secho('The module %s is installed' % module, fg='green')
        else:
            click.secho('The module %s is not installed' % module, fg='red')


@cli.command()
@click.argument('modules', nargs=-1, type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_install(ctx, modules, module, update_list):
    """Install modules"""
    __module_install(ctx, modules, module, update_list)


@cli.command()
@click.argument('modules', nargs=-1, type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def install(ctx, modules, module, update_list):
    """Install modules"""
    __module_install(ctx, modules, module, update_list)


def __module_install_all(ctx, path, update_list):
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    modules = []
    for root, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            for _root, _dirnames, _filenames in os.walk(os.path.join(root, dirname)):
                for filename in _filenames:
                    if filename in ['__openerp__.py', '__manifest__.py']:
                        modules.append(dirname)

    for module in modules:
        click.echo('Installing the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_immediate_install(module_id)
            click.secho('The module %s is installed' % module, fg='green')
        else:
            click.secho('The module %s is not installed' % module, fg='red')


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True,
                                        resolve_path=True), default=home)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def install_all(ctx, path, update_list):
    """Install modules"""
    __module_install_all(ctx, path, update_list)


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True,
                                        resolve_path=True), default=home)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_install_all(ctx, path, update_list):
    """Install modules"""
    __module_install_all(ctx, path, update_list)


def __module_upgrade(ctx, modules, module, update_list):
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    for module in Operator.unique([x.strip() for x in Operator.split_and_flat(',', modules, module)]):
        click.echo('Updating the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_immediate_upgrade(module_id)
            click.secho('The module %s is upgraded' % module, fg='green')
        else:
            click.secho('The module %s is not upgraded' % module, fg='red')


@cli.command()
@click.argument('modules', nargs=-1, type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def upgrade(ctx, modules, module, update_list):
    """Upgrade modules"""
    __module_upgrade(ctx, modules, module, update_list)


@cli.command()
@click.argument('modules', nargs=-1, type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_upgrade(ctx, modules, module, update_list):
    """Upgrade modules"""
    __module_upgrade(ctx, modules, module, update_list)


@cli.command()
@click.argument('model', type=click.STRING, required=True, nargs=-1)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True, callback=process_domain)
@click.option('--yes', is_flag=True, default=False, help="All as yes")
@click.option('--batch-mode', is_flag=True, default=False, help="Batch mode")
@click.pass_context
def truncate(ctx, model, domain, yes, batch_mode):
    """Truncate an object"""
    models = model
    odoo = ctx.obj['action_login']()
    for model in models:
        Model = odoo.env[model]
        model_ids = Model.search(domain)
        if yes or click.confirm('Are you sure you want to delete %s records from %s with the domain %s' % (
                len(model_ids), model, domain)):
            success, error = 0, 0
            if batch_mode:
                try:
                    Model.unlink(model_ids)
                    click.secho('the records are deleted', fg='green')
                    success += len(model_ids)
                except:
                    click.secho('the records can not be deleted', fg='red')
                    error += len(model_ids)

            else:
                for model_id in model_ids:
                    try:
                        Model.unlink(model_id)
                        click.secho('the record #%s is deleted' % model_id, fg='green')
                        success += 1
                    except:
                        click.secho('the record #%s can not deleted' % model_id, fg='red')
                        error += 1
            click.echo('success: %s, error: %s' % (success, error))
        else:
            click.secho('The truncate is aborted !')


def __module_uninstall(ctx, modules, module, update_list):
    odoo = ctx.obj['action_login']()
    if update_list:
        ctx.obj['update_list']()
    for module in Operator.unique([x.strip() for x in Operator.split_and_flat(',', modules, module)]):
        click.echo('Uninstalling the module : %s ' % module)
        Module = odoo.env['ir.module.module']
        module_id = Module.search([('name', '=', module)])
        if module_id:
            Module.button_uninstall(module_id)
            click.secho('The module %s is uninstalled' % module, fg='green')
        else:
            click.secho('The module %s is not uninstalled' % module, fg='red')


@cli.command()
@click.argument('modules', nargs=-1, type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def module_uninstall(ctx, modules, module, update_list):
    """Uninstall modules"""
    __module_uninstall(ctx, modules, module, update_list)


@cli.command()
@click.argument('modules', nargs=-1, type=click.STRING, required=True)
@click.option('--module', '-m', type=click.STRING, multiple=True)
@click.option('--update-list', is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def uninstall(ctx, modules, module, update_list):
    """Uninstall modules"""
    __module_uninstall(ctx, modules, module, update_list)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.argument('params', type=click.STRING, required=False)
@click.pass_context
def refs(ctx, model, params):
    """Searching the XML-IDS related to the model"""
    click.echo('Inspect the XML-IDS of the model %s ' % model)
    if '=' in model or '&' in model:
        params = model
    action_param = menu_param = view_type_param = record_id_param = False
    if params:
        for param_expression in params.split('&'):
            param_tuple = param_expression.split('=')
            if len(param_tuple) == 2:
                _k = param_tuple[0].split('#')[-1]
                _v = param_tuple[1].isdigit() and int(param_tuple[1]) or param_tuple[1]
                if _k == 'menu_id': menu_param = _v
                if _k == 'action': action_param = _v
                if _k == 'view_type': view_type_param = _v
                if _k == 'id': record_id_param = _v
                if _k == 'model': model = _v
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    xml_id = ctx.obj['xml_id']
    Action = odoo.env['ir.actions.act_window']
    Menu = odoo.env['ir.ui.menu']
    Values = odoo.env['ir.values']
    View = odoo.env['ir.ui.view']
    view_domain = [('model', '=', model)]
    if view_type_param:
        view_domain.append(('type', '=', view_type_param))
    view_ids = View.search(view_domain)
    blacklist = []
    action_domain = [('res_model', '=', model)]
    if action_param:
        action_domain.append(('id', '=', action_param))
    action_ids = Action.search(action_domain)
    if record_id_param:
        click.secho('')
        click.secho('Data XML-ID', fg='blue')
        x = PrettyTable()
        x.field_names = ["DATA XML-ID"]
        for f in x.field_names:
            x.align[f] = 'l'
        x.add_row([xml_id(odoo.env[model].browse(int(record_id_param)))])
        echo(x)

    x = PrettyTable()
    x_menu = PrettyTable()
    x.field_names = ["Action Name", "Action ID", "Action XML-ID", "Menu Name", "Menu ID", "Menu XML-ID"]
    x_menu.field_names = ["ID", "Menu Name", "Full Path"]
    for f in x.field_names:
        x.align[f] = 'l'
    for f in x_menu.field_names:
        x_menu.align[f] = 'l'
    for action in Action.browse(action_ids):
        if v(odoo.version) < v('9.0'):
            menu_domain = [('value', '=', 'ir.actions.act_window,%s' % action.id)]
            if menu_param:
                menu_domain.append(('res_id', '=', menu_param))
            values = Values.search_read(menu_domain, ['res_id'])
            menu_ids = [_x.get('res_id') for _x in values]
        else:
            menu_domain = [('action', '=', 'ir.actions.act_window,%s' % action.id)]
            if menu_param:
                menu_domain.append(('id', '=', menu_param))
            menu_ids = Menu.search(menu_domain)
        menu_data = []
        menu_ids = [_x for _x in menu_ids if _x > 0]
        for menu in Menu.browse(menu_ids):
            menu_data.append({'name': menu.name, 'id': menu.id, 'xml_id': xml_id(menu)})
            x_menu.add_row([menu.id, menu.name, menu.complete_name])
        if not menu_ids:
            menu_data.append({'name': '', 'id': '', 'xml_id': '', 'complete_name': ''})
        first_line = True
        for menu_line in menu_data:
            if first_line:
                x.add_row([action.name, action.id, xml_id(action), menu_line.get('name'), menu_line.get('id'),
                           menu_line.get('xml_id'), ])
                first_line = False
            else:
                x.add_row(['', '', '', menu_line.get('name'), menu_line.get('id'), menu_line.get('xml_id')])
    click.secho('')
    click.secho('Menus', fg='blue')
    echo(x_menu)
    click.secho('')
    click.secho('Action and menus XML-IDS', fg='blue')
    echo(x)

    for action in Action.browse(action_ids):
        click.secho('')
        click.secho('Associated views to the action : %s, xml-id : %s' % (action.name, xml_id(action)), fg='blue')
        click.secho('Context : %s' % action.context, fg='blue')
        click.secho('Domain : %s' % action.domain, fg='blue')
        associated_views = []
        x2 = PrettyTable()
        x2.field_names = ["View name", "View Type", "XML-ID"]
        for f in x2.field_names:
            x2.align[f] = 'l'
        if action.search_view_id:
            if not view_type_param or view_type_param == action.search_view_id.type:
                associated_views.append(action.search_view_id.id)
                blacklist.append(action.search_view_id.id)
        if action.view_id:
            if not view_type_param or view_type_param == action.view_id.type:
                associated_views.append(action.view_id.id)
                blacklist.append(action.view_id.id)
        for view in action.view_ids:
            if view.view_id:
                if not view_type_param or view_type_param == view.view_id.type:
                    associated_views.append(view.view_id.id)
                    blacklist.append(view.view_id.id)
        views = View.browse(list(set(associated_views)))
        for view in views:
            x2.add_row([view.name, view.type, xml_id(view)])
        echo(x2)

    click.secho('')
    click.secho('Other views', fg='blue')
    other_views = list(set(view_ids) - set(blacklist))
    views = View.browse(list(set(other_views)))
    x3 = PrettyTable()
    x3.field_names = ["View name", "View Type", "XML-ID"]
    for f in x3.field_names:
        x3.align[f] = 'l'
    for view in views:
        x3.add_row([view.name, view.type, xml_id(view)])
    echo(x3)


@cli.command()
@click.argument('field', type=click.STRING, required=True)
@click.argument('model', type=click.STRING, required=False)
@click.option('--type', type=click.STRING, required=False)
@click.pass_context
def search_field(ctx, field, model, type):
    """Searching for the views that contains the field"""
    click.echo('Search the field %s on the views of the model %s ' % (field, model))
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    xml_id = ctx.obj['xml_id']
    View = odoo.env['ir.ui.view']
    view_domain = [('arch_db', 'like', field)]
    if model:
        view_domain.append(('model', '=', model), )
    if type:
        view_domain.append(('type', '=', type), )
    view_ids = View.search(view_domain)
    views = View.browse(view_ids)
    x = PrettyTable()
    x.field_names = ["View name", "View Type", "Model", "XML-ID"]
    for f in x.field_names:
        x.align[f] = 'l'
    for view in views:
        x.add_row([view.name, view.type, view.model or '', xml_id(view)])
    echo(x)
    click.echo("Total : %s" % len(views))


@cli.command()
@click.argument('term', type=click.STRING, required=True)
@click.argument('lang', type=click.STRING, required=False)
@click.argument('module', type=click.STRING, required=False)
@click.option('--exact', is_flag=True, type=click.BOOL, default=False, required=False)
@click.pass_context
def trans_search(ctx, term, lang, module, exact):
    """Searching for the term in the translation table"""
    click.echo('Search for the term %s in the translation table' % term)
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    Translation = odoo.env['ir.translation']
    view_domain = []
    if lang:
        view_domain += [('lang', '=', lang)]
    if module:
        view_domain += [('module', '=', module)]
    if exact:
        view_domain += ['|', ('value', '=', term), ('src', '=', term)]
    else:
        view_domain += ['|', ('value', 'ilike', term), ('src', 'ilike', term)]
    item_ids = Translation.search(view_domain)
    items = Translation.browse(item_ids)
    x = PrettyTable()
    x.field_names = ["Src", "Value", "Module", "Lang", "Type", "Name"]
    for f in x.field_names:
        x.align[f] = 'l'
    for item in items:
        x.add_row([item.src, item.value, item.module, item.lang, item.type, item.name])
    echo(x)
    click.echo("Total : %s" % len(items))


@cli.command()
@click.argument('view', type=click.STRING, required=True)
@click.pass_context
def arch(ctx, view):
    """Cat the arch of the view"""
    click.echo('Show the arch of the view %s ' % view)
    odoo = ctx.obj['action_login']()
    object_from_xml_id = ctx.obj['object_from_xml_id']
    View = odoo.env['ir.ui.view']
    if view.isdigit():
        view_domain = [('id', '=', int(view))]
    else:
        view_xml_id = object_from_xml_id(view)
        if not view_xml_id:
            click.secho('XML-ID not found', fg='red')
            return
        view_domain = [('id', '=', view_xml_id.id)]
    view_ids = View.search(view_domain)
    views = View.browse(view_ids)
    for view in views:
        click.echo(view.arch)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--fields', '-f', type=click.STRING, help='Fields to show', multiple=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True, callback=process_domain)
@click.option('--limit', '-l', type=click.INT, default=0, help="Limit of records")
@click.option('--order', '-o', type=click.STRING, default='id asc', help="Expression to sort the records")
@click.option('--xmlid', is_flag=True, type=click.BOOL, default=False, help="Show XML-ID column")
@click.pass_context
def data(ctx, model, fields, domain, limit, order, xmlid):
    """Show the data of a model"""
    click.echo('Show the data of the model %s ' % model)
    odoo = ctx.obj['action_login']()
    xml_id = ctx.obj['xml_id']
    echo = ctx.obj['echo']
    Model = odoo.env[model]
    fields = ['display_name'] if not fields else fields
    records = Model.search_read(domain or [], fields, limit=limit, order=order)
    if records:
        fields = records[0].keys()
    x = PrettyTable()
    if xmlid:
        x.field_names = fields + ['XML-ID']
    else:
        x.field_names = fields
    for f in x.field_names:
        x.align[f] = 'l'
    for record in records:
        y = [record.get(f) for f in fields]
        if xmlid:
            y += [xml_id(model, record.get('id'))]
        x.add_row(y)
    echo(x)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--values', '-v', nargs=2, type=click.STRING, help='Values to apply', multiple=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True, callback=process_domain)
@click.option('--yes', is_flag=True, default=False)
@click.pass_context
def update_data(ctx, model, values, domain, yes):
    """Update the data of a model"""
    click.echo('Update the data of the model %s ' % model)
    _values = {}
    for _k, _v in values:
        try:
            _v = eval(_v)
        except:
            pass
        _values[_k] = _v
    values = _values
    odoo = ctx.obj['action_login']()
    Model = odoo.env[model]
    model_ids = Model.search(domain)
    if yes or click.confirm('Are you sure you want to update %s records from %s with the values %s' % (
            len(model_ids), model, values)):
        success, error = 0, 0
        for model_id in model_ids:
            try:
                Model.write([model_id], values)
                click.secho('the record #%s is updated' % model_id, fg='green')
                success += 1
            except:
                click.secho('the record #%s can not be updated' % model_id, fg='red')
                error += 1
        click.echo('success: %s, error: %s' % (success, error))


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--domain', '-d', nargs=3, help='Filter the records', multiple=True, callback=process_domain)
@click.pass_context
def count(ctx, model, domain):
    """Count the records on a model"""
    click.echo('Count the number of records on the model %s ' % model)
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    Model = odoo.env[model]
    nbr = Model.search_count(domain or [])
    x = PrettyTable()
    x.field_names = ['Count']
    x.align['Count'] = 'l'
    x.add_row([nbr])
    echo(x)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--user', '-u', type=click.STRING, required=False, multiple=True)
@click.pass_context
def crud(ctx, model, user):
    """List users access to the givenmodel"""
    click.echo('List the users access to the model %s ' % model)
    click.secho('', fg='blue')
    click.secho('CRUD', fg='blue')
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    User = odoo.env['res.users']
    IrRule = odoo.env['ir.rule']
    IrModelAccess = odoo.env['ir.model.access']
    ir_rule_ids = IrRule.search([('model_id.model', '=', model)])
    rule_lines = IrRule.read(ir_rule_ids)
    ir_model_access_ids = IrModelAccess.search([('model_id.model', '=', model)])
    crud_lines = IrModelAccess.read(ir_model_access_ids)
    user_ids = User.search([]) if not user else User.search([('login', 'in', user)])
    x = PrettyTable()
    x.field_names = ["Name", "Read", "Write", "Create", "Unlink"]
    x.align["Name"] = "l"
    x.align["Read"] = x.align["Write"] = x.align["Create"] = x.align["Unlink"] = "c"
    for user in User.browse(user_ids):
        name = user.name
        group_ids = map(lambda r: r.id, user.groups_id)
        filtered_crud_lines = filter(lambda r: not r.get('group_id') or r.get('group_id')[0] in group_ids, crud_lines)
        create = write = unlink = read = False
        for crud_line in filtered_crud_lines:
            read = crud_line.get('perm_read', False) or read
            write = crud_line.get('perm_write', False) or write
            unlink = crud_line.get('perm_unlink', False) or unlink
            create = crud_line.get('perm_create', False) or create
        x.add_row([name, read and 'X' or '', write and 'X' or '', create and 'X' or '', unlink and 'X' or ''])
    echo(x)
    click.secho('', fg='blue')
    click.secho('Global domains', fg='blue')
    filtered_gloabl_rule_lines = filter(lambda r: r.get('global') == True, rule_lines)
    x2 = PrettyTable()
    x2.field_names = ["Domain", "Domain Force"]
    x2.align["Domain"] = x2.align["Domain Force"] = "l"
    for line in filtered_gloabl_rule_lines:
        x2.add_row([line.get('domain', ''), line.get('domain_force', '')])
    echo(x2)
    click.secho('', fg='blue')
    click.secho('Rules', fg='blue')
    x3 = PrettyTable()
    x3.field_names = ["Name", "Domain", "Domain force", "Read", "Write", "Create", "Unlink"]
    x3.align["Name"] = x3.align["Domain"] = "l"
    x3.align["Read"] = x3.align["Write"] = x3.align["Create"] = x3.align["Unlink"] = "c"
    for user in User.browse(user_ids):
        name = user.name
        group_ids = map(lambda r: r.id, user.groups_id)
        filtered_rule_lines = filter(
            lambda r: r.get('global') == False and set(r.get('groups')).intersection(group_ids), rule_lines)
        for rule_line in filtered_rule_lines:
            domain = rule_line.get('domain', '')
            domain_force = rule_line.get('domain_force', '')
            read = rule_line.get('perm_read', False)
            write = rule_line.get('perm_write', False)
            unlink = rule_line.get('perm_unlink', False)
            create = rule_line.get('perm_create', False)
            x3.add_row([name, domain, domain_force, read and 'X' or '', write and 'X' or '', create and 'X' or '',
                        unlink and 'X' or ''])
    echo(x3)


@cli.command()
@click.argument('model', type=click.STRING, required=True)
@click.option('--show', '-s', is_flag=True, type=click.BOOL, default=False)
@click.option('--duplicates', '-d', is_flag=True, type=click.BOOL, default=False)
@click.option('--fields', '-f', is_flag=True, type=click.BOOL, default=False)
@click.option('--buttons', '-b', is_flag=True, type=click.BOOL, default=False)
@click.option('--pages', '-b', is_flag=True, type=click.BOOL, default=False)
@click.option('--xpath', '-x', type=click.STRING, default='')
@click.option('--view_id', '-i', type=click.STRING, default=None)
@click.option('--view_type', '-d', type=click.STRING, default='form')
@click.option('--attrs', '-a', type=click.STRING, default=False, multiple=True)
@click.pass_context
def view(ctx, model, show, duplicates, fields, buttons, pages, xpath, view_id, view_type, attrs):
    """Execute fields_view_get on the given model
    Extract: duplicates, xpath, buttons, pages, etc"""
    if xpath:
        xpath = '//%s[@%s=\'%s\']' % tuple(xpath.split(' ')) if len(xpath.split(' ')) == 3 else '//%s' % xpath

    def node_attrs(node):
        _node_attrs = []
        for _k, _v in node.attrib.iteritems():
            if _k in attrs:
                _node_attrs.append('%s=%s' % (_k, _v))
        return '   '.join(_node_attrs)

    def parent_xpath(node, j, node_number):
        xpath_list = []
        first = True
        while True:
            tag = node.tag
            if node.get('name'):
                tag += '[@name=\'%s\']' % node.get('name')
            if node_number > 1 and first:
                tag += '[%s]' % (j + 1)
            xpath_list.append(tag)
            node = node.getparent()
            first = False
            if node is None:
                break
        return '//' + '/'.join(xpath_list[::-1])

    """Execute fields_view_get on the given model"""
    click.echo(
        'execute the function fields_view_get on the model %s with print=%s duplicates=%s' % (model, show, duplicates))
    odoo = ctx.obj['action_login']()
    echo = ctx.obj['echo']
    object_from_xml_id = ctx.obj['object_from_xml_id']
    Model = odoo.env[model]
    fvg_args = {'view_type': view_type}
    if view_id:
        view_id = int(view_id) if view_id.isdigit() else view_id
        view_id = object_from_xml_id(view_id).id if isinstance(view_id, basestring) else view_id
        fvg_args.update({'view_id': view_id})
    xml = Model.fields_view_get(**fvg_args).get('arch')
    root = etree.fromstring(xml)
    model_fields = [f.attrib['name'] for f in root.xpath('//field') if 'name' in f.attrib]
    _fields = []
    if duplicates:
        click.secho('', fg='blue')
        click.secho('Show duplicate fields', fg='blue')
        _duplicates = []
        for f in model_fields:
            if f in _fields:
                _duplicates.append(f)
            _fields.append(f)
        x1 = PrettyTable()
        x1.field_names = ["Name"]
        x1.align["Name"] = "l"
        for _d in _duplicates:
            x1.add_row([_d])
        echo(x1)
    if show:
        click.secho('', fg='blue')
        click.secho('Show XML', fg='blue')
        click.echo(etree.tostring(root, pretty_print=True, encoding='utf-8'))
    if fields:
        click.secho('', fg='blue')
        click.secho('Show fields', fg='blue')
        x2 = PrettyTable()
        x2.field_names = ["Name", "String", "Attributes"]
        x2.align["Name"] = x2.align["Attributes"] = x2.align["String"] = "l"
        for field_item in root.xpath('//field'):
            x2.add_row([field_item.attrib.get('name', ''), field_item.attrib.get('string', ''), node_attrs(field_item)])
        echo(x2)
    if buttons:
        click.secho('', fg='blue')
        click.secho('Show buttons', fg='blue')
        x3 = PrettyTable()
        x3.field_names = ["Name", "String", "Attributes"]
        x3.align["Name"] = x3.align["Attributes"] = x3.align["String"] = "l"
        for field_item in root.xpath('//button'):
            x3.add_row([field_item.attrib.get('name', ''), field_item.attrib.get('string', ''), node_attrs(field_item)])
        echo(x3)
    if pages:
        click.secho('', fg='blue')
        click.secho('Show pages', fg='blue')
        x4 = PrettyTable()
        x4.field_names = ["Name", "String", "Attributes"]
        x4.align["Name"] = x4.align["Attributes"] = x4.align["String"] = "l"
        for field_item in root.xpath('//page'):
            x4.add_row([field_item.attrib.get('name', ''), field_item.attrib.get('string', ''), node_attrs(field_item)])
        echo(x4)
    if xpath:
        click.secho('', fg='blue')
        click.secho('Show XPATH', fg='blue')
        x5 = PrettyTable()
        x5.field_names = ["Tag", "Name", "String", "Parent XPATH"]
        x5.align["Tag"] = x5.align["Name"] = x5.align["Parent XPATH"] = x5.align["String"] = "l"
        nbr = len(root.xpath(xpath)) if root.xpath(xpath) is not None else 0
        for i, node_xpath in enumerate(root.xpath(xpath)):
            if show:
                click.echo(etree.tostring(node_xpath, pretty_print=True, encoding='utf-8'))
            else:
                x5.add_row([node_xpath.tag, node_xpath.attrib.get('name', ''), node_xpath.attrib.get('string'),
                            parent_xpath(node_xpath, i, nbr)])
        if not show:
            echo(x5)


def __check_yaml_access(ctx, data):
    database = data.get('database', False)
    host = data.get('host', False)
    load = data.get('section', False)
    mode = data.get('mode', False)
    err = False
    if database and ctx.obj['database'] and database != ctx.obj['database']:
        err = ('database', database, ctx.obj['database'])
    if host and ctx.obj['host'] and host != ctx.obj['host']:
        err = ('host', host, ctx.obj['host'])
    if mode and ctx.obj['mode'] and mode != ctx.obj['mode']:
        err = ('mode', mode, ctx.obj['mode'])
    if load and ctx.obj['load'] and load != ctx.obj['load']:
        err = ('load', load, ctx.obj['load'])
    if err:
        error("Constraint %s (%s=%s) violated" % err)


def process_yamls(ctx, name, paths):
    contents = u""
    nbr_files = 0

    def append(contents, content):
        datas = [x for x in yaml.load_all(content) if x]
        repeat = 1
        for data in datas:
            data_repeat = data.get('repeat', 0)
            repeat = data_repeat > repeat and data_repeat or repeat
            __check_yaml_access(ctx, data)
        while repeat:
            contents += u'\n---\n' + content
            repeat -= 1
        return contents

    for path in paths:
        if os.path.isfile(path):
            nbr_files += 1
            with codecs.open(path, encoding='utf8', mode='r') as yaml_file:
                contents = append(contents, yaml_file.read())
        elif os.path.isdir(path):
            new_paths = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.splitext(filename)[1].lower() in ['.yml', '.yaml']:
                        new_paths.append(filename)
            new_paths = sorted(new_paths, key=lambda k: k.strip().lower())
            for new_path in new_paths:
                nbr_files += 1
                with codecs.open(new_path, encoding='utf8', mode='r') as yaml_file:
                    contents = append(contents, yaml_file.read())
        else:
            click.secho('Can not process the path %s' % path, fg='red')
            ctx.abort()
    click.secho('%s yaml files processed' % nbr_files, fg='blue')
    return yaml.load_all(contents)


def yaml_eval(value, context):
    if not isinstance(value, basestring):
        return value
    pattern1 = re.compile("(\$\{[^}]+})")
    values1 = pattern1.findall(value)
    pattern2 = re.compile("(\$[^$]+\$)")
    values2 = pattern2.findall(value)
    pattern3 = re.compile("rand_([\s\*\$=+\.\d\w]+)_(\d+)")
    values3 = pattern3.findall(value)
    pattern4 = re.compile("pick_([^_]+)")
    values4 = pattern4.findall(value)
    if not values1 and not values2 and not values3 and not values4:
        return value
    for v_value in values1:
        main_v = v_value
        v_value = v_value[2:-1]
        try:
            v_value = unicode(eval(v_value, context))
        except:
            click.secho('Can not process %s in the context %s' % (v_value, context), fg='red')
            sys.exit(-1)
        value = value.replace(main_v, v_value)
    for v_value in values2:
        main_v = v_value
        v_value = v_value[1:-1]
        try:
            v_value = unicode(eval(v_value, context))
        except:
            click.secho('Can not process %s in the context %s' % (v_value, context), fg='red')
            sys.exit(-1)
        value = value.replace(main_v, v_value)
    for v_value in values3:
        main_v = 'rand_%s_%s' % v_value
        v_value = ''.join([pkg_random.choice(v_value[0]) for x in range(int(v_value[1]))])
        if not v_value:
            click.secho('Can not process %s' % main_v, fg='red')
            sys.exit(-1)
        value = value.replace(main_v, v_value)
    for v_value in values4:
        main_v = 'pick_%s' % v_value
        try:
            v_value = pkg_random.choice(yaml_datas.get(v_value, yaml_datas.get(v_value.lower())))
        except:
            click.secho('No yaml key %s in yaml datas' % v_value, fg='red')
            sys.exit(-1)
        if not v_value:
            click.secho('Can not process %s' % main_v, fg='red')
            sys.exit(-1)
        value = value.replace(main_v, v_value)
    if value:
        if not (re.match('\d{4}-\d{2}-\d{2}', value)):
            try:
                value = eval(value, context)
            except:
                pass
    return value


def __get_ref_records(ctx, odoo, model, ref, order, limit, context):
    kwargs = {}
    if limit:
        kwargs.update({'limit': limit})
    if order:
        kwargs.update({'order': order})
    object_from_xml_id = ctx.obj['object_from_xml_id']
    if not ref and not hasattr(ref, '__iter__'):
        return model.browse([])
    if ref == '__ALL' or (not ref and hasattr(ref, '__iter__')):
        return model.browse(model.search([], **kwargs))
    if isinstance(ref, basestring):
        ref = yaml_eval(ref, context)
    if isinstance(ref, (list, tuple)):
        new_ref = []
        for item_tuple in ref:
            x_tuple = []
            if isinstance(item_tuple, (list, tuple)):
                item_tuple_tab = []
                for sub_item_tuple in item_tuple:
                    if isinstance(sub_item_tuple, (list, tuple)):
                        xs_item = []
                        for xs_item_tuple in sub_item_tuple:
                            xs_item.append(yaml_eval(xs_item_tuple, context))
                        item_tuple_tab.append(xs_item)
                    else:
                        item_tuple_tab.append(yaml_eval(sub_item_tuple, context))
                x_tuple.append(item_tuple_tab)
            else:
                x_tuple.append(yaml_eval(item_tuple, context))
            new_ref += x_tuple
        ref = new_ref
    click.secho('Processing reference to : %s' % ref, fg='blue')
    if isinstance(ref, (int, long)):
        return model.browse([ref])
    if isinstance(ref, (list, tuple)) and isinstance(ref[0], (int, long)):
        return model.browse(ref)
    if isinstance(ref, (list, tuple)) and (ref[0] in ['&', '|', '!'] or isinstance(ref[0], (list, tuple))):
        return model.browse(model.search(ref, **kwargs))
    if IF.is_xmlid(ref):
        record = object_from_xml_id(ref)
        if not record:
            click.secho('The XML-ID %s is not found' % ref, fg='red')
            ctx.abort()
        return record
    if isinstance(ref, (list, tuple)) and isinstance(ref[0], basestring) and '.' in ref[0]:
        ids = []
        for tmp_ref in ref:
            record = object_from_xml_id(tmp_ref)
            if not record:
                click.secho('The XML-ID %s is not found' % tmp_ref, fg='red')
                ctx.abort()
            ids.append(record.id)
        return model.browse(ids)
    if isinstance(ref, basestring):
        return model.browse(model.search([('name', '=', ref)], **kwargs))
    click.secho('Can not process the reference %s' % ref, fg='red')
    ctx.abort()


INT, CHAR, TEXT, HTML, FLOAT, BOOL, SELECTION = 'integer', 'char', 'text', 'html', 'float', 'boolean', 'selection'
M2O, M2M, O2M = 'many2one', 'many2many', 'one2many'
DATE, DATETIME = 'date', 'datetime'
BINARY = 'binary'


def _onchange_spec(model, view_info=None):
    result = {}
    onchanges = []
    view_fields = []

    def process(node, info, prefix):
        if node.tag == 'field':
            name = node.attrib['name']
            names = "%s.%s" % (prefix, name) if prefix else name
            view_fields.append(name)
            if not result.get(names):
                result[names] = node.attrib.get('on_change')
                if node.attrib.get('on_change'):
                    onchanges.append(name)
            # traverse the subviews included in relational fields
            for subinfo in info['fields'][name].get('views', {}).itervalues():
                process(etree.fromstring(subinfo['arch']), subinfo, names)
        else:
            for child in node:
                process(child, info, prefix)

    if view_info is None:
        view_info = model.fields_view_get()
    process(etree.fromstring(view_info['arch']), view_info, '')
    return result, onchanges, view_fields


def __onchange_values(model, values, field_name, field_onchange):
    values = model.onchange([], values, field_name, field_onchange)
    if values and 'value' in values:
        values = values.get('value', {})
        for k, v in values.iteritems():
            if v and isinstance(v, (list, tuple)):
                v = v[0]
            values[k] = v
    return values


def __process_values(ctx, odoo, model, mode, values, fields, many2many, many2one, view_info, context):
    assert not values or isinstance(values, list), 'The values should be a list, found %s' % type(values)

    def wrap_m2m(_f, _v):
        if _f not in many2many:
            return [(6, 0, _v)]
        else:
            if many2many[_f] == 'add':
                return [(4, _x) for _x in _v]
            elif many2many[_f] == 'remove':
                return [(3, _x) for _x in _v]
            elif many2many[_f] == 'replace':
                return [(6, 0, _v)]

    vals = {}
    spec_fields, onchange_fields, view_fields = _onchange_spec(model, view_info)
    final_values = {}
    if mode == 'create':
        final_values = model.default_get(fields.keys())
    for field, value in values:
        kwargs = {}
        if field in many2one:
            kwargs = many2one.get(field)
        if field not in fields:
            click.secho('The field %s does not exists in the model %s' % (field, model._name), fg='red')
            ctx.abort()
        field_type = fields.get(field).get('type')
        field_relation = fields.get(field).get('relation')
        field_selection = fields.get(field).get('selection')
        # PROCESSINg CHAR AND TEXT
        if isinstance(value, basestring):
            value = yaml_eval(value, context)
        if field_type in [CHAR, TEXT, HTML]:
            vals[field] = unicode(value)
        elif field_type in [SELECTION]:
            for _select_key, _select_value in field_selection:
                if _select_value == value:
                    value = _select_key
            if value not in [x[0] for x in field_selection]:
                click.secho('Can not get the selection value for field %s on model %s (value: %s, allowed: %s)' % (
                    field, model._name, value, [x[0] for x in field_selection]), fg='red')
                ctx.abort()
            vals[field] = value
        elif field_type in [BOOL]:
            try:
                value = eval(value)
            except Exception as e:
                pass
            vals[field] = bool(value)
        elif field_type in [INT]:
            vals[field] = int(value)
        elif field_type in [FLOAT]:
            vals[field] = float(value)
        elif field_type in [BINARY]:
            if not os.path.isfile(value):
                click.secho('The file %s for the field %s on model %s not found' % (value, field, model._name),
                            fg='red')
                ctx.abort()
            with open(value, "rb") as binary_file:
                vals[field] = base64.b64encode(binary_file.read())
        elif field_type in [DATE]:
            if isinstance(value, date_type):
                vals[field] = value.strftime(DATE_FORMAT)
            else:
                vals[field] = dt_parser.parse(str(value), dayfirst=True, fuzzy=True).strftime(DATE_FORMAT)
        elif field_type in [DATETIME]:
            if isinstance(value, datetime):
                vals[field] = value.strftime(DATETIME_FORMAT)
            else:
                vals[field] = dt_parser.parse(str(value), dayfirst=True, fuzzy=True).strftime(DATETIME_FORMAT)
        elif field_type == M2O:
            if isinstance(value, (int, long)):
                vals[field] = value
            elif isinstance(value, basestring):
                if value == '__ALL':
                    ids = odoo.env[field_relation].search([], **kwargs)
                else:
                    ids = odoo.env[field_relation].search([('name', '=', value)], **kwargs)
                if len(ids) == 1:
                    vals[field] = ids[0]
                else:
                    click.secho('Can not get values for %s on the field %s, model %s got %s ids' % (
                        value, field, field_relation, ids), fg='red')
                    ctx.abort()
            elif isinstance(value, (list, tuple)):
                domain = []
                for line in value:
                    if len(line) != 3 and line not in ['&', '|', '!']:
                        click.secho(
                            'The tuple %s of the domain on the model %s can not be processed' % (line, model._name),
                            fg='red')
                        ctx.abort()
                    else:
                        if len(line) == 3:
                            domain.append((line[0], line[1], yaml_eval(line[2], context)))
                        else:
                            domain.append(line)
                ids = odoo.env[field_relation].search(domain, **kwargs)
                if len(ids) == 1:
                    vals[field] = ids[0]
                else:
                    click.secho('Can not get values for %s on the field %s, model %s got %s ids' % (
                        domain, field, field_relation, ids), fg='red')
                    ctx.abort()
        elif field_type == M2M:
            if isinstance(value, (int, long)):
                vals[field] = wrap_m2m(field, [value])
            elif isinstance(value, basestring):
                if value == '__ALL':
                    ids = odoo.env[field_relation].search([], **kwargs)
                    if ids:
                        vals[field] = wrap_m2m(field, ids)
                else:
                    ids = odoo.env[field_relation].search([('name', '=', value)], **kwargs)
                    if ids:
                        vals[field] = wrap_m2m(field, ids)
                    else:
                        click.secho('Can not get values for %s on the field %s, model %s got %s ids' % (
                            value, field, field_relation, ids), fg='red')
                        ctx.abort()
            elif isinstance(value, (list, tuple)):
                domain = []
                for line in value:
                    if len(line) != 3 and line not in ['&', '|', '!']:
                        click.secho(
                            'The tuple %s of the domain on the model %s can not be processed' % (line, model._name),
                            fg='red')
                        ctx.abort()
                    else:
                        if len(line) == 3:
                            domain.append((line[0], line[1], yaml_eval(line[2], context)))
                        else:
                            domain.append(line)
                ids = odoo.env[field_relation].search(domain, **kwargs)
                if ids:
                    vals[field] = wrap_m2m(field, ids)
                else:
                    click.secho('Can not get values for %s on the field %s, model %s got %s ids' % (
                        value, field, field_relation, ids), fg='red')
                    ctx.abort()
        else:
            click.secho('The type of the field %s as %s is not implemented' % (field, field_type), fg='red')
            ctx.abort()
        final_values[field] = vals[field]
        if field in onchange_fields:
            onchange_values = dict.fromkeys(view_fields, '')
            onchange_values.update(final_values)
            final_values.update(
                __onchange_values(model, onchange_values, field, spec_fields)
            )

    click.echo(final_values)
    return final_values


def __process_vars(ctx, odoo, record, context):
    datas = record.get('vars', [])
    for item in datas:
        for key, value in item.items():
            context.update({key: yaml_eval(value, context)})
    return context


def __process_message(ctx, odoo, record, context):
    datas = record.get('message', [])
    title = datas.get('title', '')
    if title:
        title = ' %s ' % title.upper()
    body = datas.get('body', '')
    click.secho(title.center(80, '*'), fg='blue')
    if body:
        click.secho(yaml_eval(body, context), fg='blue')
        click.secho('*' * 80, fg='blue')
    return context


def __process_show(ctx, odoo, record, context):
    datas = record.get('show', [])
    model_name = datas.get('model')
    model = odoo.env[model_name]
    limit = datas.get('limit', False)
    order = datas.get('order', False)
    fields = datas.get('fields', [])
    ref = datas.get('refs', False)
    records = __get_ref_records(ctx, odoo, model, ref or '__ALL', order, limit, context)
    x = PrettyTable()
    x.field_names = [f.title() for f in fields if f]
    for f in x.field_names:
        x.align[f] = "l"
    for record in records:
        x.add_row([str(getattr(record, f, '-')) for f in fields if f])
    click.echo(x)
    return context


def __process_import(ctx, odoo, record, context):
    def create_vals_from_line_and_map(line, mapping):
        vals = {}
        for dest, src in mapping.items():
            if src not in line.keys():
                error('The key %s is not found in the CSV lines' % src)
            vals[dest] = line.get(src)
        return vals

    datas = record.get('import', [])
    model_name = datas.get('model')
    model = odoo.env[model_name]
    number = datas.get('number', False)
    mapping = datas.get('map', False)
    keys = datas.get('keys', False)
    path = datas.get('path', False)
    import_random = datas.get('random', False)
    view_ref = datas.get('view_ref', False)
    pick = datas.get('pick', [])
    if not os.path.isfile(path):
        error('File %s not found' % path)
    lines = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lines.append(row)
    if not lines:
        error('No line found in the file %s' % path)
    fields = model.fields_get()
    view_info = None
    if view_ref:
        object_from_xmlid = ctx.obj['object_from_xml_id'](view_ref)
        if not object_from_xmlid:
            click.secho('Can not found the view with the XML-ID %s' % view_ref, fg='red')
            ctx.abort()
        else:
            view_info = model.fields_view_get(view_id=object_from_xmlid.id)
    number = number if number > 0 else len(lines)
    diff = number - len(lines)
    if diff > 0:
        coeff = number / len(lines) + 1
        lines *= coeff
    if import_random:
        pkg_random.shuffle(lines)
    lines = lines[:number]
    for __tmp_i, __tmp_val in enumerate(pick):
        pick[__tmp_i] = (__tmp_val.keys()[0], __tmp_val.values()[0])
    for i, line in enumerate(lines):
        values = create_vals_from_line_and_map(line, mapping)
        ref = False
        if keys:
            if set(keys) & set(values.keys()) != set(keys):
                error('Some keys on import not found in the mapping')
            ref = [['%s' % _key, '=', values.get(_key)] for _key in keys]
        records = __get_ref_records(ctx, odoo, model, ref, False, 1, context)
        values = [(k, v) for k, v in values.items() if v != '']
        values = __merge_values_and_pick(values, pick)
        if not records:
            ids = [model.create(
                __process_values(ctx, odoo, model, 'create', values, fields, {}, {}, view_info, context))]
            click.secho('Creating a record <%s> with id=%s is successful' % (model._name, ids[0],), fg='green')
            # records = model.browse(ids)
        else:
            ids = [x.id for x in records]
            records.write(
                __process_values(ctx, odoo, model, 'write', values, fields, {}, {}, view_info,
                                 context))
            click.secho('Updating %s records of <%s> is successful' % (len(ids), model._name), fg='green')
    return context


def __try_pick(field_value):
    if isinstance(field_value, basestring):
        return pkg_random.choice(glob.glob(field_value))
    else:
        return pkg_random.choice(field_value) if field_value else False


def __merge_values_and_pick(values, pick):
    vals = []
    blacklist = []
    if values:
        for field_name, field_value in values:
            blacklist.append(field_name)
            vals.append((field_name, field_value))
    if pick:
        for field_name, field_value in pick:
            if field_name in blacklist:
                continue
            vals.append((field_name, __try_pick(field_value)))
    return vals


def __process_record(ctx, odoo, record, context):
    data = record.get('record', {})
    model_name = data.get('model')
    model = odoo.env[model_name]
    # SET VARS
    ALLOWED_TYPOLOGIES = ['model', 'one', 'multi', 'last', 'first']
    # GET DEFAULT PARAMS
    typology = data.get('typology', 'multi')
    context.update(data.get('context', {}))
    unlink = data.get('unlink', False)
    values = data.get('values', [])
    pick = data.get('pick', [])
    create = data.get('create', True)
    update = data.get('update', data.get('write', True))
    order = data.get('order', False)
    limit = data.get('limit', False)
    exports = data.get('export', [])
    many2many = data.get('many2many', [])
    many2one = data.get('many2one', [])
    model_key = data.get('key', '')
    model_key = model_key.strip().lower() + '_' if model_key else ''
    functions = data.get('functions', [])
    workflows = data.get('workflows', [])
    view_ref = data.get('view_ref', False)
    ref = data.get('ref', data.get('refs', False))
    # ASSERTION
    assert model_name, 'No model name given'
    assert typology in ALLOWED_TYPOLOGIES, 'The typology %s should be in %s' % (typology, ALLOWED_TYPOLOGIES)
    assert isinstance(many2many, (list, tuple)), 'The many2many should be a list (-)'
    assert isinstance(values, (list, tuple)), 'The values should be a list (-)'
    tmp_many2many = {}
    for tm2m_item in many2many:
        for tm2m_data in tm2m_item.items():
            tm2m_data = list(tm2m_data)
            assert len(tm2m_data) == 2, 'Error on many2many format'
            assert tm2m_data[1] in ['add', 'keep', 'remove', 'erase',
                                    'replace'], 'In many2many the accepted values are: add, remove and replace'
            if tm2m_data[1] in ['add', 'keep']:
                tm2m_data[1] = 'add'
            elif tm2m_data[1] in ['remove', 'erase']:
                tm2m_data[1] = 'remove'
            elif tm2m_data[1] in ['replace']:
                tm2m_data[1] = 'replace'
            tmp_many2many[tm2m_data[0]] = tm2m_data[1]
    many2many = tmp_many2many
    assert isinstance(many2many, dict), 'The many2many should be a dictionnary'
    tmp_many2one = {}
    for tm2o_item in many2one:
        for tm2o_field in tm2o_item.keys():
            tmp_many2one[tm2o_field] = {}
            for tm2on_value in tm2o_item[tm2o_field]:
                tmp_many2one[tm2o_field].update(tm2on_value)
    many2one = tmp_many2one
    assert isinstance(many2one, dict), 'The many2one should be a dictionnary'
    view_info = None
    if view_ref:
        object_from_xmlid = ctx.obj['object_from_xml_id'](view_ref)
        if not object_from_xmlid:
            click.secho('Can not found the view with the XML-ID %s' % view_ref, fg='red')
            ctx.abort()
        else:
            view_info = model.fields_view_get(view_id=object_from_xmlid.id)
    # PROCESSING VALUES
    for __tmp_i, __tmp_val in enumerate(values):
        values[__tmp_i] = (__tmp_val.keys()[0], __tmp_val.values()[0])
    for __tmp_i, __tmp_val in enumerate(pick):
        pick[__tmp_i] = (__tmp_val.keys()[0], __tmp_val.values()[0])
    values = __merge_values_and_pick(values, pick)
    records = __get_ref_records(ctx, odoo, model, ref, order, limit, context)
    if data.get('show', []):
        show_fields = data.get('show') if isinstance(data.get('show'), (list, tuple)) else ['id', 'display_name']
        px = PrettyTable()
        px.field_names = [x.title() for x in show_fields]
        for f in px.field_names:
            px.align[f] = "l"
        for px_record in records:
            px.add_row([getattr(px_record, f, '-') for f in show_fields])
        click.echo(px)
    # PROCESSING UNLINK
    if unlink:
        try:
            records.unlink()
            click.secho('Unlink is successful', fg='green')
        except:
            click.secho('Unlink is fail', fg='red')
        records = model
    # PROCESSING CREATE AND WRITE
    if values:
        fields = model.fields_get()
        if not records:
            if create:
                ids = [model.create(
                    __process_values(ctx, odoo, model, 'create', values, fields, many2many, many2one, view_info,
                                     context))]
                click.secho('Creating a record <%s> with id=%s is successful' % (model._name, ids[0],), fg='green')
                records = model.browse(ids)
            else:
                click.secho('Skip creating a record <%s>' % (model._name,), fg='yellow')
        else:
            if update:
                ids = [x.id for x in records]
                records.write(
                    __process_values(ctx, odoo, model, 'write', values, fields, many2many, many2one, view_info,
                                     context))
                click.secho('Updating %s records of <%s> is successful' % (len(ids), model._name), fg='green')
            else:
                click.secho('Skip updating records of <%s>' % (model._name,), fg='yellow')
    # PROCESSING TYPOLOGIES
    if typology == 'one':
        if records:
            records = records[0]
        else:
            click.secho('Can not force the typology=%s, records=%s' % (typology, len(records)), fg='green')
            ctx.abort()
    elif typology == 'last':
        if records:
            records = records[-1]
        else:
            click.secho('Can not force the typology=%s, records=%s' % (typology, len(records)), fg='green')
            ctx.abort()
    elif typology == 'first':
        if records:
            records = records[0]
        else:
            click.secho('Can not force the typology=%s, records=%s' % (typology, len(records)), fg='green')
            ctx.abort()
    elif typology == 'model':
        if records:
            records = records[0:0]
        else:
            click.secho('Can not force the typology=%s, records=%s' % (typology, len(records)), fg='green')
            ctx.abort()
    ids = [x.id for x in records]
    # PROCESSING FUNCTIONS
    for func_line in functions:
        func_name = func_line.get('name')
        func_args = func_line.get('args', {})
        func_api = func_line.get('api', 'multi')
        func_kwargs = func_line.get('kwargs', True)
        args = {}
        func_res = False
        for arg_key, arg_value in func_args.items():
            args[arg_key] = yaml_eval(arg_value, context)
        if func_api == 'multi':
            rec = records
            click.secho('Execute the function %s on %s with params %s' % (func_name, rec, args), fg='blue')
            if func_kwargs:
                func_res = getattr(rec, func_name)(**args)
            else:
                func_res = getattr(rec, func_name)(*args.values())
        elif func_api == 'one':
            for rec in records:
                click.secho('Execute the function %s on %s with params %s' % (func_name, rec, args), fg='blue')
                if func_kwargs:
                    func_res = getattr(rec, func_name)(**args)
                else:
                    func_res = getattr(rec, func_name)(*args.values())
        elif func_api == 'model':
            rec = model
            click.secho('Execute the function %s on %s with params %s' % (func_name, rec, args), fg='blue')
            if func_kwargs:
                func_res = getattr(rec, func_name)(**args)
            else:
                func_res = getattr(rec, func_name)(*args.values())
        context.update({"%s_%s%s" % (model._name.replace('.', '_'), model_key, func_name): func_res})
    for wkf in workflows:
        click.secho('Execute the signal %s on the records' % (wkf, records), fg='blue')
        model.signal_workflow([x.id for x in records], wkf)
    for export_line in exports:
        for export_key, export_expr in export_line.items():
            context[export_key] = eval(export_expr, {
                'record': records[0] if len(records) > 0 else False,
                'records': records,
                'ids': ids,
                'model': model,
                'odoo': odoo,
                'env': odoo.env,
            })
    export_model_record_key = "%s_%srecord" % (model._name.replace('.', '_'), model_key)
    export_model_records_key = "%s_%srecords" % (model._name.replace('.', '_'), model_key)
    context.update({
        '%s' % export_model_record_key: records[0] if len(records) > 0 else False,
        '%s_id' % export_model_record_key: records[0].id if len(records) > 0 else False,
        '%s' % export_model_records_key: records,
    })
    return context


@cli.command()
@click.argument('datas', type=click.STRING, required=True, nargs=-1, callback=process_yamls)
@click.pass_context
def yaml_load(ctx, datas):
    """Process yaml files"""
    odoo = ctx.obj['action_login']()
    blocks = []
    datas = [data for data in datas if data]
    for data in datas:
        validate(data, SCHEMA_GLOBAL)
    for data in datas:
        if not data:
            continue
        if not isinstance(data, dict):
            click.secho('A block is ignored, continue', fg='yellow')
        block = data.copy()
        blocks.append(block)
    context = dict(
        odoo.env.context,
        today=datetime.now().strftime(DATE_FORMAT),
        now=datetime.now().strftime(DATETIME_FORMAT),
    )
    for block in blocks:
        if 'record' in block:
            context.update(__process_record(ctx, odoo, block, context))
        if 'vars' in block:
            context.update(__process_vars(ctx, odoo, block, context))
        if 'message' in block:
            context.update(__process_message(ctx, odoo, block, context))
        if 'show' in block:
            context.update(__process_show(ctx, odoo, block, context))
        if 'import' in block:
            context.update(__process_import(ctx, odoo, block, context))


@cli.command()
@click.pass_context
def yaml_template(ctx):
    """Show an example"""
    example = """
---
vars:
    - var1: ici la valeur de var1
    - var2: pick_PRODUCT            #Pick from the dictionnary
    - var3: rand_ICIALLCHARS_4      #Pick randomely 4 chars
---
message:
    title: Title
    body: |
        Here the body
        It can contain $var1$ and ${var2}
---
record:
    model: res.partner
    refs: Accepts domain [[...]], xml-id, __ALL, name and ID  # else a new record will created if values
    order: id asc             # used by refs
    limit: 1                  # used by refs
    view_ref: xmlid of the view to force playing the onchanges
    pick:                     # Like default values
        customer: [True, False]
        ref: ['a','b','c']
        reference: sequence
        image: /ll/*/images/man-*.*  #blob
    values:                   # many2many and one2many accepts domains, ID, filter by name
        - field1: value1
        - field2: value2
    create: True              # create a record with values if not found
    update: True              # update records with values
    unlink: True              # unlinks records
    typology: one|multi|multi|last|first   # slice records, Used for functions and workflows
                                           # default multi
    functions:
        - 
            name: func1
            args:
                arg1: val1
                arg2: val2
            api: model|multi|one
            kwargs: False
        - 
            name: func2
            args:
                arg1: val2
                arg2: val
        # auto export model_name_func_nameg
    workflows:
        - signal1
        - signal2
    export:
        - record_id: record.id
        - test_name: record.name
    show:
        - field1
        - field2
    many2many:
        - fieldm2m: add(default)|remove|replace    
    many2one:
        - fieldm2o: 
            - limit: 1
            - order: name desc
    context:                               # add keys/values to the context of variables
        key1: val1
        key2: val2
---
import:
  model: res.partner
  path: path/partners.csv
  view_ref: XML-ID
  pick:                     # Like default values
      customer: [True, False]
      ref: ['a','b','c']
      reference: sequence
      image: /ll/*/images/man-*.*  #blob
  map:
      name: nom
      street: adresse
      country_id: pays
      lang: langue
      customer: client
      supplier: fournisseur
  keys:
    - name
  number: 2
  random: True
    """
    click.echo(example)


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
