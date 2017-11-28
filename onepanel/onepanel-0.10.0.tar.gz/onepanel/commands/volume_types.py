import click

from onepanel.commands.base import APIViewController


class VolumeTypeViewController(APIViewController):

    def __init__(self, conn):

        super(VolumeTypeViewController, self).__init__(conn)

        self.endpoint = '{root}/volume_types'.format(
            root=self.conn.URL
        )


@click.group(help='Available volume types')
@click.pass_context
def volume_types(ctx):

    ctx.obj['view_controller'] = VolumeTypeViewController(ctx.obj['connection'])


@volume_types.command(
    'list',
    help='Show available volume types and their IDs'
)
@click.pass_context
def list_volume_types(ctx):

    vc = ctx.obj['view_controller']

    items = vc.get()
    vc.print_items(items)

