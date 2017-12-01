from globus_cli.parsing import globus_group

from globus_cli.commands.endpoint.role.list import role_list
from globus_cli.commands.endpoint.role.show import role_show
from globus_cli.commands.endpoint.role.create import role_create
from globus_cli.commands.endpoint.role.delete import role_delete


@globus_group(name='role', help='Manage endpoint roles')
def role_command():
    pass


role_command.add_command(role_list)
role_command.add_command(role_show)
role_command.add_command(role_create)
role_command.add_command(role_delete)
