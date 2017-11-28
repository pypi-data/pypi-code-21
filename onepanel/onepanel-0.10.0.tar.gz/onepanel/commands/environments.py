"""
Machine types commands
"""
from prettytable import PrettyTable

import click


@click.group(help='Environment (machine types) commands group')
@click.pass_context
def environments(ctx):
    pass


@environments.command('list', help='Show available environments')
@click.pass_context
def list_environments(ctx):

    conn = ctx.obj['connection']

    url = '{root}/instance_templates?instance_type=mod'.format(
        root=conn.URL
    )

    r = conn.get(url)
    if r.status_code == 200:
        resp = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return

    # Make a summary table

    if len(resp) == 0:
        print('No available environments')
        return list()

    summary = PrettyTable(border=False)
    summary.field_names = ['ID', 'ENVIRONMENT']
    summary.align = 'l'
    for environment in resp:
        summary.add_row([environment['uid'], environment['name']])
    print(summary)

    return [environment['uid'] for environment in resp]

