"""
Machine types commands
"""
from prettytable import PrettyTable

import click


@click.group(help='Machine (hardware) commands group')
@click.pass_context
def machine_types(ctx):
    pass


@machine_types.command('list', help='Show available machine types')
@click.pass_context
def list_machine_types(ctx):

    conn = ctx.obj['connection']

    url = '{root}/machine_types'.format(
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
        print('No available machine types')
        return list()

    summary = PrettyTable(border=False)
    summary.field_names = ['ID', 'SPECS']
    summary.align = 'l'
    for machine_type in resp:
        summary.add_row([machine_type['uid'], machine_type['name']])
    print(summary)

    return [machine_type['uid'] for machine_type in resp]

