import click

from globus_cli.parsing import common_options, endpoint_id_arg
from globus_cli.safeio import formatted_print
from globus_cli.services.auth import lookup_identity_name
from globus_cli.services.transfer import get_client


@click.command('list', help='List of permissions on an endpoint')
@common_options
@endpoint_id_arg
def list_command(endpoint_id):
    """
    Executor for `globus endpoint permission list`
    """
    client = get_client()

    rules = client.endpoint_acl_list(endpoint_id)

    def principal_str(rule):
        principal = rule['principal']
        if rule['principal_type'] == 'identity':
            username = lookup_identity_name(principal)

            return username or principal
        elif rule['principal_type'] == 'group':
            return (u'https://www.globus.org/app/groups/{}'
                    ).format(principal)
        else:
            principal = rule['principal_type']

        return principal

    formatted_print(
        rules, fields=[('Rule ID', 'id'), ('Permissions', 'permissions'),
                       ('Shared With', principal_str), ('Path', 'path')])
