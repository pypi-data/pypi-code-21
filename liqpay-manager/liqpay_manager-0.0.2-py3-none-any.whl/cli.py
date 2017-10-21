#! /usr/bin/env python

from datetime import datetime, timedelta
from warnings import catch_warnings

import click
from envparse import Env

import urllib3

from . import manager as lq_mgr


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with catch_warnings(record=True):
    Env.read_envfile('~/.liqpay_secrets')
    Env.read_envfile()

DATE_FORMAT = '%Y-%m-%d'

ENV_VAR_PREFIX = 'LQ_PAY_'
ENV_VAR_TMPL = '{prefix}{{var_name}}'.format(prefix=ENV_VAR_PREFIX)


def validate_date(ctx, param, value):
    return datetime.strptime(value, DATE_FORMAT)


def print_api_result(result_obj):
    click.echo(result_obj)
    result = result_obj['result']
    click.echo(f"Result: {result}")

    if result == 'error':
        for err_field in ('err_code', 'err_description', 'code', 'status', 'is_3ds'):
            click.echo(f"{err_field.title()}: {result_obj[err_field]}")
        return

    try:
        result_data = result_obj['data']
    except KeyError:
        click.echo('API returned no data')
        return

    if result_data:
        click.echo('Result data:')
        for result_row in result_data:
            click.echo(result_row)
    else:
        click.echo('No matching results returned')


@click.group()
@click.option('--public-key', prompt=True, envvar=ENV_VAR_TMPL.format(var_name='PUBKEY'))
@click.option('--private-key', prompt=True, envvar=ENV_VAR_TMPL.format(var_name='SECRET'))
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj.update(kwargs)


@cli.command()
@click.option('--date-from', callback=validate_date, prompt='Start date [format: {}]:'.format(DATE_FORMAT))
@click.option('--date-to', callback=validate_date, prompt='End date [format: {}]:'.format(DATE_FORMAT))
@click.pass_context
def list_transactions(ctx, date_from, date_to):
    date_from_ts = int(date_from.timestamp())
    date_to_ts = int((date_to + timedelta(days=1)).timestamp())

    api_creds = ctx.obj['public_key'], ctx.obj['private_key']

    api_request_args = {
        'date_from': date_from_ts,
        'date_to': date_to_ts,
    }

    with lq_mgr.LiqPayAPI(*api_creds) as lq_api:
        transactions_list = lq_api.reports(**api_request_args)

    print_api_result(transactions_list)


@cli.command()
@click.option('--order-id', prompt=True, type=str)
@click.pass_context
def cancel_subscription(ctx, order_id):
    api_creds = ctx.obj['public_key'], ctx.obj['private_key']

    api_request_args = {
        'order_id': order_id,
    }

    with lq_mgr.LiqPayAPI(*api_creds) as lq_api:
        unsubscribe_result = lq_api.unsubscribe(**api_request_args)

    print_api_result(unsubscribe_result)


def main():
    return cli(obj={}, auto_envvar_prefix=ENV_VAR_PREFIX)


__name__ == '__main__' and main()
