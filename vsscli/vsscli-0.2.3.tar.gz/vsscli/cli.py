import os
import click
from click_repl import repl
from vsscli import __history_file_path__
from prompt_toolkit.history import FileHistory
from . import (__version__, __config_file_path__,
               __env_vars__, __default_endpoint__,
               __default_debug_mode__)
from pyvss import __version__ as __pyvss_version__
from vsscli.VssCLI import CLIManager, VssCLIError, VssError
from vsscli.utils import (columns_two_kv, print_vm_info,
                          print_tokens,
                          print_requests,
                          print_request, print_vm_attr,
                          print_vm_objects_attr,
                          print_os, print_morefs, print_objects,
                          print_object, pretty_print, get_all_inv_attrs)
from vsscli.utils import (validate_email, validate_schedule,
                          validate_phone_number, validate_admin,
                          validate_inform,
                          validate_json_type)

try:
    from webdav import client as wc
    from webdav.client import WebDavException
    HAS_WEBDAV = True
except ImportError:
    HAS_WEBDAV = False


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    v = ['vsscli/{}'.format(__version__),
         'pyvss/{}'.format(__pyvss_version__)]
    click.echo(' '.join(v))
    ctx.exit()


@click.group()
@click.option('-f', '--offline', is_flag=True,
              help='Work in offline mode.')
@click.option('-d', '--debug', is_flag=True,
              envvar=__env_vars__.get('debug'),
              help='Debug mode on')
@click.option('-o', '--output',
              type=click.Choice(['json', 'text']),
              envvar=__env_vars__.get('output'),
              help='The formatting style for command output. '
                   'This can be configured '
                   'by the VSS_DEFAULT_OUTPUT environment variable.')
@click.option('-c', '--config', type=str, required=False,
              envvar=__env_vars__.get('config'),
              help='Path to configuration file. This can be configured '
                   'by the VSS_CONFIG_FILE environment variable.'
              )
@click.option('-e', '--endpoint', type=str,
              help='VSS REST API endpoint or configure by setting '
                   'VSS_API_ENDPOINT environment variable.')
@click.option('-v', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.pass_context
def main_cli(ctx, offline, debug, output, config, endpoint):
    """The VSS Command Line Interface is a unified tool
     to manage your EIS Virtual Cloud services."""
    config = config or __config_file_path__
    cli_manager = CLIManager(offline=offline,
                             output=output,
                             click=click,
                             config=config,
                             debug=debug)
    # validate if a different endpoint is set
    epon_env = __env_vars__.get('endpoint')
    endpoint = endpoint or os.environ.get(epon_env,
                                          __default_endpoint__)
    cli_manager.update_endpoints(endpoint)
    ctx.obj['CLIManager'] = cli_manager


@main_cli.group(invoke_without_command=True)
@click.option('-u', '--username', type=str,
              help='VSS username or configure by setting VSS_API_USER'
                   ' environment variable.')
@click.option('-p', '--password', type=str,
              help='VSS password or configure by setting VSS_API_USER_PASS'
                   ' environment variable.')
@click.option('-e', '--endpoint', type=str,
              help='VSS REST API endpoint or configure by setting '
                   'VSS_API_ENDPOINT environment variable.')
@click.pass_context
def configure(ctx, username, password, endpoint):
    """Configure VSS CLI options. If this command is run with no arguments,
    you will be prompted for configuration values such as your VSS username
    and password.  If your config file does not  exist (the default location
    is ~/.vss/config.json), the VSS CLI will create it for you."""
    user_env = __env_vars__.get('user')
    pass_env = __env_vars__.get('pass')
    epon_env = __env_vars__.get('endpoint')
    if ctx.invoked_subcommand is None:
        endpoint = endpoint if endpoint \
            else click.prompt('Endpoint',
                              default=os.environ.get(epon_env,
                                                     __default_endpoint__),
                              type=str)
        username = username if username \
            else click.prompt('Username',
                              default=os.environ.get(user_env, ''),
                              type=str)
        password = password if password \
            else click.prompt('Password',
                              default=os.environ.get(pass_env, ''),
                              show_default=False, hide_input=True,
                              type=str,
                              confirmation_prompt=True)
        cli_manager = ctx.obj['CLIManager']
        # string is required instead of unicode
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        try:
            cli_manager.configure(username=username,
                                  password=password,
                                  endpoint=endpoint)
        except VssError as ex:
            raise VssCLIError(ex.message)


@configure.command('ls', short_help='show config')
@click.pass_context
def configure_list(ctx):
    """Shows existing configuration."""
    cli_manager = ctx.obj['CLIManager']
    profiles = cli_manager.load_raw_config_file()
    _profiles = list()
    from base64 import b64decode
    for key, profile in profiles.items():
        user, pwd = b64decode(profile['auth']).split(':')
        masked_pwd = ''.join(['*' for i in range(len(pwd))])
        _profiles.append({'endpoint': key,
                          'user': user, 'pass': masked_pwd[:8],
                          'token': '{}...{}'.format(profile['token'][:10],
                                                    profile['token'][-10:]),
                          'source': 'config file'})
    # validate if user/pass/endpoint/token are set
    __env_vars__.pop('config')
    __env_vars__.pop('output')
    envs = [e for e in __env_vars__.values() if e in os.environ]
    if envs:
        user = os.environ.get(__env_vars__.get('user'), '')
        pwd = os.environ.get(__env_vars__.get('pass'), '')
        masked_pwd = ''.join(['*' for i in range(len(pwd))])
        tk = os.environ.get(__env_vars__.get('token'), '')
        endpoint = os.environ.get(__env_vars__.get('endpoint'), '')
        source = 'env'
        _profiles.append({'endpoint': endpoint,
                          'user': user, 'pass': masked_pwd,
                          'token': '{}...{}'.format(tk[:10], tk[-10:]),
                          'source': source})

    if not cli_manager.output_json:
        lines = print_objects(_profiles, False, False, 'profile',
                              ['endpoint', 'user', 'pass', 'token', 'source'])
    else:
        lines = pretty_print(_profiles)
    click.echo(lines)


@main_cli.command()
@click.option('-i', '--history', type=str,
              help='File path to save history',
              default=os.path.expanduser(__history_file_path__),
              required=False)
@click.pass_context
def shell(ctx, history):
    """REPL interactive shell"""
    welcome = """
    __   _____ ___
    \ \ / / __/ __|      Tab-completion & suggestions
     \ V /\__ \__ \\      Prefix external commands with "!"
      \_/ |___/___/      History will be saved: {history}
       CLI v{version}

    Exit shell with :exit, :q, :quit, ctrl+d
    """.format(version=__version__, history=history)
    click.echo(welcome)
    dir_name = os.path.dirname(__history_file_path__)
    # create dir for history
    if not os.path.exists(os.path.expanduser(dir_name)):
        os.mkdir(os.path.expanduser(dir_name))
    try:
        prompt_kwargs = {
            'history': FileHistory(history),
            'message': u'vss > '
        }
        repl(ctx, prompt_kwargs=prompt_kwargs)
    except RuntimeError as ex:
        raise VssCLIError(ex.message)


@main_cli.group(help='Manage your API tokens')
@click.pass_context
def token(ctx):
    cli_manager = ctx.obj['CLIManager']
    if not cli_manager.offline:
        cli_manager.load_config()


@token.command('get',
               help='Display user token info.')
@click.argument('id', type=int, required=True)
@click.pass_context
def token_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        _token = cli_manager.get_user_token(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_object(_token, key='tk'))
        else:
            lines = pretty_print(_token)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@token.command('rm',
               help='Delete user token.')
@click.argument('id', type=int, required=True, nargs=-1)
@click.option('-s', '--summary', is_flag=True,
              help='Print request summary')
@click.pass_context
def token_rm(ctx, id, summary):
    cli_manager = ctx.obj['CLIManager']
    try:
        _request = list()
        with click.progressbar(id) as ids:
            for i in ids:
                _request.append(cli_manager.delete_user_token(i))
        if summary:
            for r in _request:
                if not cli_manager.output_json:
                    lines = '\n'.join(print_object(r, key='tk'))
                else:
                    lines = pretty_print(r)
                click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@token.command('ls',
               help='List user tokens.')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def token_ls(ctx, filter, page, sort, no_header, quiet,
             show_all, count):
    """List tokens based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: valid,eq,false

            vss token ls -f valid,eq,false

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss token ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        tks = cli_manager.get_user_tokens(show_all=show_all,
                                          per_page=count,
                                          **params)
        if not cli_manager.output_json:
            lines = print_tokens(tks, no_header, quiet)
        else:
            lines = pretty_print(tks)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group(short_help='Manage your VSS account')
@click.pass_context
def account(ctx):
    """Manage your VSS account"""
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@account.group('get',
               short_help='get account attribute')
@click.pass_context
def account_get(ctx):
    """Obtain an account attribute"""
    pass


@account.group('set',
               short_help='set account attribute')
@click.pass_context
def account_set(ctx):
    """Set account attribute"""
    pass


@account_set.command('notification')
@click.option('-a', '--all', is_flag=True,
              help='Enables all email notification')
@click.option('-n', '--none', is_flag=True,
              help='Disables all email notification')
@click.option('-e', '--error', is_flag=True,
              help='Enables error notification only')
@click.pass_context
def account_set_notification(ctx, all, none, error):
    """Customize email notification settings"""
    cli_manager = ctx.obj['CLIManager']
    try:
        if all:
            cli_manager.enable_user_email()
        elif none:
            cli_manager.disable_user_email()
        elif error:
            cli_manager.enable_user_email_error()
        else:
            raise click.UsageError('Select at least one option: '
                                   '-a/--all -n/--none or -e/--error')
        notification = cli_manager.get_user_email_settings()
        if not cli_manager.output_json:
            _lines = print_request(notification)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(notification)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('status')
@click.pass_context
def account_get_status(ctx):
    """Account status"""
    cli_manager = ctx.obj['CLIManager']
    try:
        status = cli_manager.get_user_status()
        if not cli_manager.output_json:
            _lines = print_request(status)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(status)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('groups')
@click.pass_context
def account_get_groups(ctx):
    """User groups"""
    cli_manager = ctx.obj['CLIManager']
    try:
        groups = dict(groups=cli_manager.get_user_groups())
        if not cli_manager.output_json:
            _lines = print_request(groups)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(groups)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('group')
@click.argument('group_name', type=str, required=True)
@click.option('-m', '--member', is_flag=True, help='show group members',
              default=False)
@click.pass_context
def account_get_group(ctx, group_name, member):
    """Get given group info or members. User must be part of the group."""
    cli_manager = ctx.obj['CLIManager']
    try:
        group = cli_manager.get_user_group(group_name, member)
        if member:
            group = group.get('uniqueMember')
            _lines = print_objects(group, False, False, 'uid', ['uid', 'cn'])
        else:
            _lines = print_request(group)

        if not cli_manager.output_json:
            lines = _lines if member else '\n'.join(_lines)
        else:
            lines = pretty_print(group)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('notification')
@click.pass_context
def account_get_notification(ctx):
    """User notification settings"""
    cli_manager = ctx.obj['CLIManager']
    try:
        notification = cli_manager.get_user_email_settings()
        if not cli_manager.output_json:
            _lines = print_request(notification)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(notification)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('access-role')
@click.pass_context
def account_get_access_role(ctx):
    """Access role and entitlements"""
    cli_manager = ctx.obj['CLIManager']
    try:
        roles = cli_manager.get_user_roles()
        roles = roles['access']
        if not cli_manager.output_json:
            _lines = print_request(roles)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(roles)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('request-role')
@click.pass_context
def account_get_request_role(ctx):
    """Request role and entitlements"""
    cli_manager = ctx.obj['CLIManager']
    try:
        roles = cli_manager.get_user_roles()
        roles = roles['request']
        if not cli_manager.output_json:
            _lines = print_request(roles)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(roles)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@account_get.command('personal')
@click.pass_context
def account_get_personal(ctx):
    """User information"""
    cli_manager = ctx.obj['CLIManager']
    try:
        personal = cli_manager.get_user_personal()
        ldap = cli_manager.get_user_ldap()
        personal.update(ldap)
        if not cli_manager.output_json:
            _lines = print_request(personal)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(personal)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group('request')
@click.pass_context
def request_mgmt(ctx):
    """Manage your different requests history.
    Useful to track request status and details."""
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@request_mgmt.group('image-sync')
@click.pass_context
def request_image_sync_mgmt(ctx):
    """Manage user image synchronization requests.

    Synchronizing your personal store files with the VSS API produces a
    image-sync request"""
    pass


@request_image_sync_mgmt.command('ls', short_help='list image-sync requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_image_sync_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                               show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request image-sync ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request image-sync ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_image_sync_requests(show_all=show_all,
                                                        per_page=count,
                                                        **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet,
                                   table_header=['id', 'created_on',
                                                 'updated_on', 'status',
                                                 'type'])
        else:
            lines = pretty_print(_requests)

        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_image_sync_mgmt.command('get', help='Image sync request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_image_sync_mgmt_get(ctx, id):
    try:
        cli_manager = ctx.obj['CLIManager']
        request = cli_manager.get_image_sync_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('snapshot')
@click.pass_context
def request_snapshot_mgmt(ctx):
    """Manage virtual machine snapshot requests.

    Creating, deleting and reverting virtual machine snapshots will produce
    a virtual machine snapshot request."""
    pass


@request_snapshot_mgmt.group('set', help='Update snapshot request')
@click.argument('request_id', type=int, required=True)
@click.pass_context
def request_snapshot_mgmt_set(ctx, request_id):
    if ctx.invoked_subcommand is None:
        raise click.UsageError('Sub command is required.')
    try:
        ctx.obj['ID'] = request_id
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_snapshot_mgmt_set.command('duration')
@click.option('-l', '--lifetime', type=click.IntRange(1, 72),
              help='Number of hours the snapshot will live.',
              required=True)
@click.pass_context
def request_snapshot_mgmt_set_duration(ctx, lifetime):
    try:
        cli_manager = ctx.obj['CLIManager']
        request_id = ctx.obj['ID']
        _ = cli_manager.get_snapshot_request(request_id)
        _, request = cli_manager.extend_snapshot_request(request_id,
                                                         lifetime)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_snapshot_mgmt.command('ls', short_help='list snapshot requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_snapshot_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                             show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request snapshot ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request snapshot ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_snapshot_requests(show_all=show_all,
                                                      per_page=count,
                                                      **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_snapshot_mgmt.command('get', help='Snapshot request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_snapshot_mgmt_get(ctx, id):
    try:
        cli_manager = ctx.obj['CLIManager']
        request = cli_manager.get_snapshot_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('export')
@click.pass_context
def request_export_mgmt(ctx):
    """Manage virtual machine export requests."""
    pass


@request_export_mgmt.command('ls', short_help='list vm export requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_export_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                           show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request export ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request export ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_export_requests(show_all=show_all,
                                                    per_page=count,
                                                    **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_export_mgmt.command('get', short_help='Export request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_export_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_export_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('inventory')
@click.pass_context
def request_inventory_mgmt(ctx):
    """Manage virtual machine inventory requests."""
    pass


@request_inventory_mgmt.command('ls', short_help='list inventory requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_inventory_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                              show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request inventory ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request inventory ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_inventory_requests(show_all=show_all,
                                                       per_page=count,
                                                       **params)
        # text or json output
        if not cli_manager.output_json:
            table_header = ['id', 'created_on', 'updated_on', 'status',
                            'name', 'format']
            lines = print_requests(_requests, no_header, quiet,
                                   table_header=table_header)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_inventory_mgmt.command('get', short_help='Inventory request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_inventory_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_inventory_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('folder',
                    help='Logical folder requests.')
@click.pass_context
def request_folder_mgmt(ctx):
    """Manage your logical folder requests.

    Logical Folders are containers for storing and organizing
    inventory objects, in this case virtual machines."""
    pass


@request_folder_mgmt.command('ls', short_help='list logical folder requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_folder_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                           show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request folder ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request folder ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_folder_requests(show_all=show_all,
                                                    per_page=count,
                                                    **params)
        # text or json output
        if not cli_manager.output_json:
            table_header = ['id', 'created_on', 'updated_on', 'status',
                            'action', 'moref']
            lines = print_requests(_requests, no_header, quiet,
                                   table_header=table_header)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_folder_mgmt.command('get', short_help='Folder request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_change_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_folder_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('change')
@click.pass_context
def request_change_mgmt(ctx):
    """Manage your virtual machine change requests.

    Updating any virtual machine attribute will produce a virtual machine
    change request."""
    pass


@request_change_mgmt.command('ls', short_help='list vm change requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_change_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                           show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request change ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request change ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_change_requests(show_all=show_all,
                                                    per_page=count,
                                                    **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_change_mgmt.command('get', short_help='Change request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_change_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_change_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_change_mgmt.command('retry', short_help='Retry vm change request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_change_mgmt_retry(ctx, id):
    """Retries given virtual machine change request with status
    'Error Processed'.
    """
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.retry_change_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_mgmt.group('new')
@click.pass_context
def request_new_mgmt(ctx):
    """Manage your new virtual machine deployment requests."""
    pass


@request_new_mgmt.command('get', short_help='New vm request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_new_mgmt_get(ctx, id):
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.get_new_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_new_mgmt.command('ls', short_help='list new vm requests')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def request_new_mgmt_ls(ctx, filter, page, sort, no_header, quiet,
                        show_all, count):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss request new ls -f status,eq,Processed

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss request new ls -s created_on,desc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _requests = cli_manager.get_new_requests(show_all=show_all,
                                                 per_page=count,
                                                 **params)
        # text or json output
        if not cli_manager.output_json:
            lines = print_requests(_requests, no_header, quiet)
        else:
            lines = pretty_print(_requests)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@request_new_mgmt.command('retry', short_help='Retry vm new request')
@click.argument('id', type=int, required=True)
@click.pass_context
def request_new_mgmt_retry(ctx, id):
    """Retries given virtual machine new request with status
    'Error Processed'.
    """
    cli_manager = ctx.obj['CLIManager']
    try:
        request = cli_manager.retry_new_request(id)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group()
@click.pass_context
def misc(ctx):
    """Miscellaneous utilities"""


@misc.command('hash-string',
              short_help='Hashes string using SHA-512')
@click.argument('string_to_hash', type=str, required=False)
@click.pass_context
def misc_hash_string(ctx, string_to_hash):
    """Hashes string using SHA-512. If string_to_hash argument
    not provided, input will be prompted. Useful to create hashed
    passwd entries."""
    from pyvss.helper import hash_string
    string_to_hash = string_to_hash or click.prompt(
        'String', show_default=False, hide_input=True,
        confirmation_prompt=True)
    click.echo(hash_string(string_to_hash))


@misc.command('gz-b64e',
              short_help='Compresses and encodes a given string')
@click.argument('string_gz_encode', type=str, required=True)
@click.pass_context
def misc_encode_gz(ctx, string_gz_encode):
    """Compresses (gz) and encodes in base64 a given string."""
    from pyvss.helper import compress_encode_string
    click.echo(compress_encode_string(string_gz_encode))


@misc.command('b64d-gz',
              short_help='Decompress and decodes a given string')
@click.argument('string_gz_encoded', type=str, required=True)
@click.pass_context
def misc_decodes_ugz(ctx, string_gz_encoded):
    """Compresses (gz) and encodes in base64 a given string."""
    from pyvss.helper import decode_uncompress_string
    click.echo(decode_uncompress_string(string_gz_encoded))


@main_cli.group()
@click.pass_context
def compute(ctx):
    """Compute related resources such as virtual machines, networks
       supported operating systems, logical folders, OVA/OVF images,
       floppy images, ISO images and more."""
    cli_manager = ctx.obj['CLIManager']
    cli_manager.load_config()


@compute.group('domain', short_help='List domains available')
@click.pass_context
def compute_domain(ctx):
    """A fault domain consists of one or more ESXI hosts and
    Datastore Clusters grouped together according to their
    physical location in the datacenter."""


@compute_domain.command('ls', short_help='list fault domains')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name or moref')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only morefs')
@click.pass_context
def compute_domain_ls(ctx, filter, page, no_header, quiet):
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        folders = cli_manager.get_domains(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(folders, no_header, quiet, 'moref',
                                  ['moref', 'name'])
        else:
            lines = pretty_print(folders)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_domain.group('get', help='Given domain info.',
                      invoke_without_command=True)
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_domain_get(ctx, moref):
    try:
        ctx.obj['MOREF'] = str(moref)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            domain = cli_manager.get_domain(moref)
            if not cli_manager.output_json:
                _lines = print_object(domain, 'moref',
                                      ['status',
                                       'hostsCount',
                                       'name'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(domain)
            click.echo(lines)
        pass
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_domain_get.command('vms',
                            short_help='list virtual machines.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_domain_get_vms(ctx, page, no_header, quiet):
    """List logical folder children virtual machines."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        domain = cli_manager.get_domain(
            moref, summary=1)
        vms = domain['vms']
        if not cli_manager.output_json:
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  ['uuid', 'name'])
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('inventory', short_help='Manage inventory reports')
@click.pass_context
def compute_inventory(ctx):
    """Create or download an inventory file of your virtual machines
    hosted. Inventory files are created and transferred to your VSKEY-STOR
    space and are also available through the API."""
    pass


@compute_inventory.command('dl', short_help='download inventory report')
@click.argument('request_id', type=int, required=True)
@click.option('-d', '--dir', type=str, help='report destination',
              required=False,
              default=None)
@click.option('-l', '--launch', is_flag=True,
              help='Launch link in default application')
@click.pass_context
def compute_inventory_dl(ctx, request_id, dir, launch):
    """Downloads given inventory request to current directory or
    provided path. Also, it's possible to open downloaded file in
    default editor."""
    try:
        cli_manager = ctx.obj['CLIManager']
        file_path = cli_manager.download_inventory_result(
            request_id=request_id, directory=dir)
        request = {'file': file_path}
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
        if launch:
            click.launch(file_path)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_inventory.command('mk', short_help='create inventory')
@click.argument('attribute', nargs=-1, default=None)
@click.option('-f', '--format', type=click.Choice(['json', 'csv']),
              default='csv', help='hide header')
@click.option('-a', '--all', is_flag=True, help='include all attributes')
@click.pass_context
def compute_inventory_mk(ctx, format, all, attribute):
    """Submits an inventory report request resulting in a file with your
    virtual machines and more than 30 attributes in either JSON or CSV
    format.

    The following attributes can be requested in the report:

    status, domain, diskCount, uuid, nics, state, dnsName, vmtRunning,
    memory, provisionedSpace, osId, folder, snapshot,
    requested, networkIds, hardwareVersion, changeLog,
    ha_group, usedSpace, nicCount, uncommittedSpace,
    name, admin, disks, vmtVersion, inform, client,
    guestOsId, clientNotes, ipAddress, cpu
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        _attributes = get_all_inv_attrs()
        attributes = _attributes.keys() if all else list(attribute)
        request = cli_manager.create_inventory_file(fmt=format,
                                                    props=attributes)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('floppy', short_help='Manage floppy images.')
@click.pass_context
def compute_floppy(ctx):
    """Available floppy images in both the VSS central store and your personal
    VSKEY-STOR space."""
    pass


@compute_floppy.group('public', short_help='Browse public images')
@click.pass_context
def compute_floppy_public(ctx):
    """Available Floppy images in the VSS central store"""
    pass


@compute_floppy_public.command('ls', short_help='list floppy images')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by path or name')
@click.option('-s', '--sort', type=unicode,
              help='sort by name or path')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_floppy_public_ls(ctx, filter, sort, page, quiet, no_header):
    """List available Floppy images in the VSS central store.

    Filter by path or name path=<path> or name=<name>. For example:

        vss compute floppy ls -f name like,pv% -s path asc
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(expand=1)
        if filter:
            query_params['filter'] = '{},{}'.format(filter[0], filter[1])
        if sort:
            query_params['sort'] = '{},{}'.format(sort[0], sort[1])
        # query
        images = cli_manager.get_floppies(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_floppy.group('personal', short_help='Browse current user images')
@click.pass_context
def compute_floppy_personal(ctx):
    """Available Floppy images in your personal VSKEY-STOR space."""
    pass


@compute_floppy_personal.command('ls',
                                 short_help='list personal Floppy images')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_floppy_personal_ls(ctx, page, quiet, no_header):
    """List available Floppy images stored in your personal VSKEY-STOR space.
    If the image you uploaded is not listing here, use the sync and try again.

        vss compute floppy personal sync
        vss compute floppy personal ls
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        # query
        images = cli_manager.get_user_floppies()
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_floppy_personal.command('sync',
                                 short_help='Sync personal Floppy images')
@click.pass_context
def compute_floppy_personal_sync(ctx):
    """Synchronize ISO images stored in your personal VSKEY-STOR space. Once
    processed it should be listed with the ls command."""
    try:
        cli_manager = ctx.obj['CLIManager']
        # request
        request = cli_manager.sync_user_floppies()
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('iso', short_help='Manage ISO images.')
@click.pass_context
def compute_iso(ctx):
    """Available ISO images in both the VSS central store and your personal
    VSKEY-STOR space."""
    pass


@compute_iso.group('public', short_help='Browse public images')
@click.pass_context
def compute_iso_public(ctx):
    """Available ISO images in the VSS central store"""
    pass


@compute_iso_public.command('ls',
                            short_help='list public ISO images')
@click.option('-f', '--filter', type=(unicode, unicode),
              default=(None, None),
              help='filter list by path or name')
@click.option('-s', '--sort', type=(unicode, unicode),
              default=(None, None),
              help='sort by name or path')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_iso_public_ls(ctx, filter, sort, page, quiet, no_header):
    """List available ISO images in the VSS central store.

    Filter by name and sort desc. For example:

        vss compute iso ls -f name like,Cent% -s path asc
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(expand=1)
        if filter:
            query_params['filter'] = '{},{}'.format(filter[0], filter[1])
        if sort:
            query_params['sort'] = '{},{}'.format(sort[0], sort[1])
        # query
        images = cli_manager.get_isos(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_iso.group('personal', short_help='Browse current user images')
@click.pass_context
def compute_iso_personal(ctx):
    """Available ISO images in your personal VSKEY-STOR space."""
    pass


@compute_iso_personal.command('ls',
                              short_help='list personal ISO images')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_iso_personal_ls(ctx, page, quiet, no_header):
    """List available ISO images stored in your personal VSKEY-STOR space.
    If the image you uploaded is not listing here, use the sync and try again.

        vss compute iso personal sync
        vss compute iso personal ls
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        # query
        images = cli_manager.get_user_isos()
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_iso_personal.command('sync', short_help='Sync personal ISO images')
@click.pass_context
def compute_iso_personal_sync(ctx):
    """Synchronize ISO images stored in your personal VSKEY-STOR space. Once
    processed it should be listed with the ls command."""
    try:
        cli_manager = ctx.obj['CLIManager']
        # request
        request = cli_manager.sync_user_isos()
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@main_cli.group()
@click.option('-u', '--username', type=str,
              help='VSS username or configure by setting VSS_API_USER'
                   ' environment variable or defaults to configuration file.')
@click.option('-p', '--password', type=str,
              help='VSS password or configure by setting VSS_API_USER_PASS'
                   ' environment variable or defaults to configuration file.')
@click.pass_context
def stor(ctx, username, password):
    """Manage your personal storage space"""
    cli_manager = ctx.obj['CLIManager']
    user_env = __env_vars__.get('user')
    pass_env = __env_vars__.get('pass')
    try:
        user, passwd, tk = cli_manager.load_config()
        username = user or username or click.prompt(
            'Username',
            default=os.environ.get(user_env, ''))
        password = password or passwd or click.prompt(
            'Password', default=os.environ.get(pass_env, ''),
            show_default=False, hide_input=True,
            confirmation_prompt=True)
        ctx.obj[user_env] = username
        ctx.obj[pass_env] = password
        if not HAS_WEBDAV:
            raise VssCLIError('Python webdav client module is required.'
                              'Install it by running: '
                              'pip install webdavclient')
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('ul', short_help='upload file')
@click.argument('file_path', type=click.Path(exists=True),
                required=True)
@click.option('-d', '--dir', type=str,
              help='Remote target directory',
              default='/')
@click.option('-n', '--name', type=str,
              help='Remote target name')
@click.pass_context
def stor_ul(ctx, file_path, name, dir):
    """Upload given file to your VSKEY-STOR space.
    This command is useful when, for instance, a required ISO is
    not available in the VSS central repository and needs to be
    mounted to a virtual machine.
    """
    try:
        cli_manager = ctx.obj['CLIManager']

        file_name = name or os.path.basename(file_path)
        remote_base = dir
        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        # check if remote path exists
        if not cli_manager.vskey_stor.check(remote_base):
            cli_manager.vskey_stor.mkdir(remote_base)
        # upload
        remote_path = os.path.join(remote_base, file_name)
        click.echo('Upload {} to {} in progress... '.format(file_path,
                                                            remote_path))
        cli_manager.vskey_stor.upload_sync(
            remote_path=remote_path,
            local_path=file_path)
        click.echo('Upload complete.')
        # result
        obj = cli_manager.vskey_stor.info(remote_path)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('dl', short_help='download file')
@click.argument('remote_path', type=str, required=True)
@click.option('-d', '--dir', type=str,
              help='Local target directory')
@click.option('-n', '--name', type=str,
              help='Local target name')
@click.pass_context
def stor_dl(ctx, remote_path, dir, name):
    """Download remote file."""
    try:
        cli_manager = ctx.obj['CLIManager']

        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        local_dir = os.path.expanduser(dir) or os.getcwd()
        local_name = name or os.path.basename(remote_path)
        local_path = os.path.join(local_dir, local_name)
        # check if remote path exists
        if not cli_manager.vskey_stor.check(remote_path):
            raise VssCLIError('Remote path not found {}'.format(remote_path))
        # upload
        click.echo('Download {} to {} in progress... '.format(remote_path,
                                                              local_path))
        cli_manager.vskey_stor.download_sync(
            remote_path=remote_path,
            local_path=local_path)
        click.echo('Download complete.')
        # result
        obj = cli_manager.vskey_stor.info(remote_path)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('ls', short_help='list remote dir contents')
@click.argument('remote_path', type=str, default='/')
@click.pass_context
def stor_ls(ctx, remote_path):
    try:
        cli_manager = ctx.obj['CLIManager']

        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        # result
        items = cli_manager.vskey_stor.list(remote_path)
        obj = dict(items=items)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@stor.command('get', short_help='get remote info')
@click.argument('remote_path', type=str, required=True)
@click.pass_context
def stor_get(ctx, remote_path):
    try:
        cli_manager = ctx.obj['CLIManager']

        cli_manager.get_vskey_stor(
            webdav_login=ctx.obj['VSS_API_USER'],
            webdav_password=ctx.obj['VSS_API_USER_PASS'])
        # result
        obj = cli_manager.vskey_stor.info(remote_path)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(obj))
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except WebDavException as ex:
        raise VssCLIError(str(ex))
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('image', short_help='Manage your OVA/OVF images.')
@click.pass_context
def compute_image(ctx):
    """Available OVA/OVF images in both the VSS central store and your personal
    VSKEY-STOR space."""
    pass


@compute_image.group('public', short_help='Browse public images')
@click.pass_context
def compute_image_public(ctx):
    """Available OVA/OVF images in the VSS central store"""
    pass


@compute_image_public.command('ls', short_help='list OVA/OVF images')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='Filter list by path or name')
@click.option('-s', '--sort', type=unicode,
              help='sort by name or path')
@click.option('-p', '--page', is_flag=True,
              help='Page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_image_public_ls(ctx, filter, sort, page, quiet, no_header):
    """List available OVA/OVF VM images in the VSS central store.

    Filter by name and sort desc. For example:

        vss compute image ls -f name like,Cent% -s path asc
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(expand=1)
        if filter:
            query_params['filter'] = '{},{}'.format(filter[0], filter[1])
        if sort:
            query_params['sort'] = '{},{}'.format(sort[0], sort[1])
        # query
        images = cli_manager.get_images(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_image.group('personal', short_help='Browse current user images')
@click.pass_context
def compute_image_personal(ctx):
    """Available OVA/OVF VM images in your personal VSKEY-STOR space."""
    pass


@compute_image_personal.command('ls',
                                short_help='list personal OVA/OVF VM images')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only path')
@click.pass_context
def compute_image_personal_ls(ctx, page, quiet, no_header):
    """List available OVA/OVF VM images stored in your personal VSKEY-STOR space.
    If the image you uploaded is not listing here, use the sync and try again.

        vss compute image personal sync
        vss compute image personal ls
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        # query
        images = cli_manager.get_user_vm_images()
        if not cli_manager.output_json:
            lines = print_objects(images, no_header, quiet, 'path',
                                  ['path', 'name'])
        else:
            lines = pretty_print(images)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_image_personal.command('sync',
                                short_help='Sync personal OVA/OVF VM images')
@click.pass_context
def compute_iso_personal_sync(ctx):
    """Synchronize OVA/OVF VM images stored in your personal VSKEY-STOR space. Once
    processed it should be listed with the ls command."""
    try:
        cli_manager = ctx.obj['CLIManager']
        # request
        request = cli_manager.sync_user_images()
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('folder')
@click.pass_context
def compute_folder(ctx):
    """Manage logical folders.

    Logical Folders are containers for storing and organizing
    inventory objects, in this case virtual machines."""
    pass


@compute_folder.command('ls', short_help='list folders')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name, moref or parent')
@click.option('-s', '--sort', type=unicode,
              help='sort by name or moref.'
                   'attributes.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only morefs')
@click.pass_context
def compute_folder_ls(ctx, filter, sort, page, quiet, no_header):
    """List logical folders.

    Filter by path or name name=<name>, moref=<moref>, parent=<parent>.
    For example:

        vss compute folder ls -f name Project
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        if sort:
            query_params['sort'] = sort
        # query
        folders = cli_manager.get_folders(**query_params)
        if not cli_manager.output_json:
            lines = print_objects(folders, no_header, quiet, 'moref',
                                  ['moref', 'name', 'parent', 'path'])
        else:
            lines = pretty_print(folders)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder.group('set', short_help='update folder')
@click.argument('moref', type=str)
@click.pass_context
def compute_folder_set(ctx, moref):
    """Update given folder attribute."""
    if ctx.invoked_subcommand is None:
        raise click.UsageError('Sub command is required.')
    try:
        ctx.obj['MOREF'] = str(moref)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder_set.command('parent', short_help='move folder')
@click.argument('parent_moref', type=str, required=True)
@click.pass_context
def compute_folder_set_parent(ctx, parent_moref):
    """Move folder to given moref.
     Use to obtain parent folder:

       vss compute folder ls

    """
    try:
        cli_manager = ctx.obj['CLIManager']
        folder_moref = str(ctx.obj['MOREF'])
        # exist folder and target
        _ = cli_manager.get_folder(folder_moref)
        _ = cli_manager.get_folder(parent_moref)
        request = cli_manager.move_folder(folder_moref,
                                          parent_moref)

        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder_set.command('name', short_help='rename folder')
@click.argument('name', type=str, required=True)
@click.pass_context
def compute_folder_set_name(ctx, name):
    """Rename folder to given name.
     Use to obtain parent folder:

       vss compute folder ls

    """
    try:
        cli_manager = ctx.obj['CLIManager']
        folder_moref = str(ctx.obj['MOREF'])
        # exist folder and target
        _ = cli_manager.get_folder(folder_moref)
        # submit request
        request = cli_manager.rename_folder(folder_moref,
                                            name)

        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder.command('mk', short_help='create folder')
@click.argument('name', type=str, required=True)
@click.option('-p', '--parent', type=str,
              help='Parent folder',
              required=True)
@click.pass_context
def compute_folder_mk(ctx, parent, name):
    """Create a logical folder under a given moref parent.
    Use to obtain parent folder:

       vss compute folder ls

    """
    try:
        cli_manager = ctx.obj['CLIManager']
        parent = str(parent)
        cli_manager.get_folder(parent)
        request = cli_manager.create_folder(moref=parent,
                                            name=name)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder.group('get', help='Given folder info.',
                      invoke_without_command=True)
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_folder_get(ctx, moref):
    try:
        ctx.obj['MOREF'] = str(moref)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            folder = cli_manager.get_folder(moref)
            if not cli_manager.output_json:
                _lines = print_object(folder, 'folder',
                                      ['path',
                                       'parent', 'name'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(folder)
            click.echo(lines)
        pass
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder_get.command('vms',
                            short_help='list virtual machines.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_folder_get_vms(ctx, page, no_header, quiet):
    """List logical folder children virtual machines."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        folder = cli_manager.get_folder(
            moref, summary=1)
        vms = folder['vms']
        if not cli_manager.output_json:
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  ['uuid', 'name'])
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_folder_get.command('perm',
                            short_help='list permissions.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_folder_get_perms(ctx, page, no_header, quiet):
    """Obtain logical folder group or user permissions."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        perms = cli_manager.get_folder_permission(moref)
        if not cli_manager.output_json:
            lines = print_objects(perms, no_header, quiet, 'principal',
                                  ['principal', 'group', 'propagate'])
        else:
            lines = pretty_print(perms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('net')
@click.pass_context
def compute_network(ctx):
    """List available virtual networks."""
    pass


@compute_network.command('ls', short_help='list virtual networks.')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name or moref')
@click.option('-s', '--sort', type=unicode,
              help='sort by name or moref.'
                   'attributes.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_network_ls(ctx, filter, sort, page, quiet, no_header):
    """List available virtual networks.

    Filter by path or name name=<name> or moref=<moref>.
    For example:

        vss compute net ls -f name public
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        query_params = dict(summary=1)
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        if sort:
            query_params['sort'] = sort
        # query
        nets = cli_manager.get_networks(**query_params)
        if not cli_manager.output_json:
            lines = print_morefs(nets, no_header, quiet,
                                 table_header=['moref', 'name',
                                               'description', 'subnet',
                                               'ports'])
        else:
            lines = pretty_print(nets)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_network.group('get', help='Given virtual network info.',
                       invoke_without_command=True)
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_network_get(ctx, moref):
    try:
        ctx.obj['MOREF'] = str(moref)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            net = cli_manager.get_network(moref)
            if not cli_manager.output_json:
                _lines = print_object(
                    net, 'net', ['name',
                                 'accessible', 'ports',
                                 'description', 'admin', 'subnet',
                                 'client'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(net)
            click.echo(lines)
        pass
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_network_get.command('vms',
                             short_help='list virtual machines')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_network_get_vms(ctx, quiet, no_header, page):
    """List virtual machines using current network."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        net = cli_manager.get_network(
            moref, summary=1)
        vms = net['vms']
        if not cli_manager.output_json:
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  ['uuid', 'name'])
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_network_get.command('perm',
                             short_help='list permissions.')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_network_get_perms(ctx, page, no_header, quiet):
    """Obtain network group or user permissions."""
    try:
        moref = str(ctx.obj['MOREF'])
        cli_manager = ctx.obj['CLIManager']
        perms = cli_manager.get_network_permission(moref)
        if not cli_manager.output_json:
            lines = print_objects(perms, no_header, quiet, 'principal',
                                  ['principal', 'group', 'propagate'])
        else:
            lines = pretty_print(perms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('os', short_help='Supported OS.')
@click.pass_context
def compute_os(ctx):
    """Supported operating systems by our infrastructure.
    This resource is useful when deploying a new or
    reconfiguring an existing virtual machine."""
    pass


@compute_os.command('ls', short_help='list operating systems')
@click.option('-f', '--filter', type=unicode,
              help='apply filter')
@click.option('-s', '--sort', type=unicode,
              help='apply sorting ')
@click.option('-a', '--show-all', is_flag=True,
              help='show all results')
@click.option('-c', '--count', type=int,
              help='size of results')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only id')
@click.pass_context
def compute_os_ls(ctx, filter, page, sort, show_all, count,
                  no_header, quiet):
    """List requests based on:

        Filter list in the following format <field_name>,<operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.
        For example: status,eq,Processed

            vss compute os ls -f guestFullName,like,CentOS%

        Sort list in the following format <field_name>,<asc|desc>. For example:

            vss compute os ls -s guestId,asc

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        params = dict()
        if filter:
            params['filter'] = filter
        if sort:
            params['sort'] = sort
        _os = cli_manager.get_os(show_all=show_all,
                                 per_page=count,
                                 **params)
        if not cli_manager.output_json:
            lines = print_os(_os, no_header, quiet)
        else:
            lines = pretty_print(_os)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('template')
@click.pass_context
def compute_template(ctx):
    """List virtual machine templates"""
    pass


@compute_template.command('ls', short_help='List virtual machine templates.')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='Filter list by name, ip, dns or path.')
@click.option('-s', '--summary', is_flag=True,
              help='Display summary.')
@click.option('-p', '--page', is_flag=True,
              help='Page results in a less-like format.')
@click.option('-n', '--no-header', is_flag=True,
              help='Hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only uuid')
@click.pass_context
def compute_template_ls(ctx, filter, summary, page, quiet, no_header):
    """List virtual machine templates.

    Filter list by name, ip address dns or path. For example:

        vss compute template ls -f name VMTemplate1

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        query_params = dict()
        if summary:
            query_params['summary'] = 1
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        # query
        templates = cli_manager.get_templates(**query_params)
        if not cli_manager.output_json:
            if summary:
                for t in templates:
                    t['folder'] = '{parent} > {name}'.format(**t['folder'])
                attributes = ['uuid', 'name', 'folder',
                              'cpuCount', 'memoryGB',
                              'powerState', 'guestFullName']
            else:
                attributes = ['uuid', 'name']
            lines = print_objects(templates, no_header, quiet, 'uuid',
                                  attributes)
        else:
            lines = pretty_print(templates)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute.group('vm')
@click.pass_context
def compute_vm(ctx):
    """Manage virtual machines. List, update, deploy and delete instances."""
    pass


@compute_vm.command('ls', short_help='list virtual machines')
@click.option('-f', '--filter', multiple=True, type=(unicode, unicode),
              help='filter list by name, ip, dns or path')
@click.option('-s', '--summary', is_flag=True,
              help='display summary')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.option('-o', '--sort', type=unicode,
              help='sort by name or uuid. If summary is enabled, sort by more '
                   'attributes.')
@click.pass_context
def compute_vm_ls(ctx, filter, summary, page, quiet, sort, no_header):
    """List virtual machine instances.

        Filter and sort list by name, ip address dns or path. For example:

        vss compute vm ls -f name VM -s -o name

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        query_params = dict()
        if summary:
            query_params['summary'] = 1
        if filter:
            for f in filter:
                query_params[f[0]] = f[1]
        if sort:
            query_params['sort'] = sort
        # query
        vms = cli_manager.get_vms(**query_params)
        if not cli_manager.output_json:
            if summary:
                for t in vms:
                    t['folder'] = '{parent} > {name}'.format(**t['folder'])
                attributes = ['uuid', 'name', 'folder',
                              'cpuCount', 'memoryGB',
                              'powerState', 'guestFullName']
            else:
                attributes = ['uuid', 'name']
            lines = print_objects(vms, no_header, quiet, 'uuid',
                                  attributes)
        else:
            lines = pretty_print(vms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('get', short_help='Given virtual machine info.',
                  invoke_without_command=True)
@click.argument('uuid', type=click.UUID, required=True)
@click.pass_context
def compute_vm_get(ctx, uuid):
    """Obtain virtual machine summary and other attributes."""
    try:
        ctx.obj['UUID'] = str(uuid)
        if ctx.invoked_subcommand is None:
            cli_manager = ctx.obj['CLIManager']
            vm = cli_manager.get_vm(uuid=uuid)
            if not cli_manager.output_json:
                _lines = print_vm_info(vm)
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(vm)
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('stats',
                        short_help='Performance statistics')
@click.argument('type', type=click.Choice(['memory', 'io',
                                           'cpu', 'net']))
@click.pass_context
def compute_vm_get_stats(ctx, type):
    """Get virtual machine memory, io, cpu and network
     performance statistics. Choose between: io, memory,
     cpu or net. For example:

    vss compute vm get <uuid> stats memory
    """
    try:
        uuid = ctx.obj['UUID']
        cli_manager = ctx.obj['CLIManager']
        if not cli_manager.is_powered_on_vm(uuid):
            raise VssError('Cannot perform operation in current power state')
        lookup = {'cpu': cli_manager.get_vm_performance_cpu,
                  'memory': cli_manager.get_vm_performance_memory,
                  'io': cli_manager.get_vm_performance_io,
                  'net': cli_manager.get_vm_performance_net}
        stats = lookup[type](uuid=uuid)
        if not cli_manager.output_json:
            _lines = print_object(stats, 'name', stats.keys())
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(stats)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('perm',
                        short_help='Permissions')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_vm_get_perms(ctx, page, no_header, quiet):
    """Obtain virtual machine group or user permissions."""
    try:
        uuid = ctx.obj['UUID']
        cli_manager = ctx.obj['CLIManager']
        perms = cli_manager.get_vm_permission(uuid)
        if not cli_manager.output_json:
            lines = print_objects(perms, no_header, quiet, 'principal',
                                  ['principal', 'group', 'propagate'])
        else:
            lines = pretty_print(perms)
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('extra-config',
                        short_help='GuestInfo extra configs')
@click.pass_context
def compute_vm_extra_config(ctx):
    """Get virtual machine guest info via VMware Tools."""
    try:
        cli_manager = ctx.obj['CLIManager']
        objs = cli_manager.get_vm_extra_config(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], objs)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(objs)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('snapshot',
                        short_help='Snapshots')
@click.argument('snapshot_id', type=int, required=False)
@click.pass_context
def compute_vm_get_snapshot(ctx, snapshot_id):
    try:
        cli_manager = ctx.obj['CLIManager']
        if snapshot_id:
            snap = cli_manager.get_vm_snapshot(ctx.obj['UUID'], snapshot_id)
            if not cli_manager.output_json:
                _lines = print_vm_attr(ctx.obj['UUID'], snap[0],
                                       ['id',
                                        'name',
                                        'description',
                                        'sizeGB',
                                        'createTime',
                                        'age'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(snap)
        else:
            snaps = cli_manager.get_vm_snapshots(ctx.obj['UUID'])
            if not cli_manager.output_json:
                _lines = print_vm_objects_attr(ctx.obj['UUID'], snaps,
                                               ['id', 'name'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(snaps)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('guest',
                        short_help='Guest summary')
@click.pass_context
def compute_vm_get_guest(ctx):
    """Get virtual machine guest info via VMware Tools."""
    try:
        cli_manager = ctx.obj['CLIManager']
        obj = cli_manager.get_vm(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], obj,
                                   [('guest', 'guestFullName'),
                                    ('guest', 'guestId'),
                                    ('guest', 'hostName'),
                                    ('guest', 'ipAddress'),
                                    ('guest', 'toolsStatus')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('guest-ip',
                        short_help='Guest IP configuration')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_vm_get_guest_ip(ctx, page, no_header, quiet):
    """Get virtual machine ip addresses via VMware Tools."""
    try:
        cli_manager = ctx.obj['CLIManager']
        objs = cli_manager.get_vm_guest_ip(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_objects(objs, no_header, quiet, 'ipAddress',
                                   ['ipAddress', 'macAddress',
                                    'origin', 'state'])
            lines = _lines
        else:
            lines = pretty_print(objs)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('change-log',
                        short_help='Change log')
@click.option('-p', '--page', is_flag=True,
              help='page results in a less-like format')
@click.option('-n', '--no-header', is_flag=True,
              help='hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='display only uuid')
@click.pass_context
def compute_vm_get_change_log(ctx, page, no_header, quiet):
    """Get virtual machine change log."""
    try:
        cli_manager = ctx.obj['CLIManager']
        objs = cli_manager.get_vm_vss_changelog(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_objects(objs, no_header, quiet, 'request_id',
                                   ['request_id', 'attribute', 'dateTime',
                                    'username', 'value'])
            lines = _lines
        else:
            lines = pretty_print(objs)
        # paging
        if page:
            click.echo_via_pager(lines)
        else:
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('boot',
                        short_help='Boot configuration')
@click.pass_context
def compute_vm_get_boot(ctx):
    """Virtual machine boot settings. Including boot delay and
    whether to boot and enter directly to BIOS."""
    try:
        cli_manager = ctx.obj['CLIManager']
        obj = cli_manager.get_vm_boot(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], obj,
                                   ['enterBIOSSetup',
                                    'bootRetryDelayMs',
                                    'bootDelayMs'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(obj)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('usage',
                        short_help='Usage (Metadata)')
@click.pass_context
def compute_vm_get_usage(ctx):
    """Get current virtual machine usage.

    Part of the VSS metadata and the name prefix (YYMMP-) is composed
    by the virtual machine usage, which is intended to specify
    whether it will be hosting a Production, Development,
    QA, or Testing system."""
    try:
        cli_manager = ctx.obj['CLIManager']
        usage = cli_manager.get_vm_vss_usage(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], usage,
                                   ['value'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(usage)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('client',
                        short_help='Client (Metadata)')
@click.pass_context
def compute_vm_get_client(ctx):
    """Get current virtual machine client/billing department.
    Part of the VSS metadata.
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        usage = cli_manager.get_vm_vss_client(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], usage,
                                   ['value'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(usage)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('ha-group',
                        short_help='HA Group (Metadata)')
@click.option('-v', '--vms', is_flag=True,
              help='Display vm status')
@click.option('-n', '--no-header', is_flag=True,
              help='Hide header')
@click.option('-q', '--quiet', is_flag=True,
              help='Display only uuid')
@click.pass_context
def compute_vm_get_ha_group(ctx, vms, no_header, quiet):
    try:
        cli_manager = ctx.obj['CLIManager']
        ha = cli_manager.get_vm_vss_ha_group(ctx.obj['UUID'])
        if cli_manager.output not in ['json']:
            if vms:
                lines = print_objects(ha['vms'], no_header, quiet,
                                      'uuid', ['uuid', 'name', 'valid'])
            else:
                _lines = print_vm_attr(ctx.obj['UUID'], ha,
                                       ['count', 'valid'])
                lines = '\n'.join(_lines)
        else:
            if vms:
                lines = pretty_print(ha['vms'])
            else:
                ha.pop('vms', None)
                lines = pretty_print(ha)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('consolidate',
                        short_help='Consolidation requirement')
@click.pass_context
def compute_vm_get_consolidate(ctx):
    """Virtual Machine disk consolidation status."""
    try:
        cli_manager = ctx.obj['CLIManager']
        consolidate = cli_manager.get_vm_consolidation(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], consolidate,
                                   ['requireDiskConsolidation'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(consolidate)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('inform',
                        short_help='Informational contacts (Metadata)')
@click.pass_context
def compute_vm_get_inform(ctx):
    """Virtual machine informational contacts. Part of the
    VSS metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        inform = cli_manager.get_vm_vss_inform(ctx.obj['UUID'])
        inform = dict(inform=inform)
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], inform, ['inform'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(inform)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('spec',
                        short_help='Configuration specification')
@click.pass_context
def compute_vm_get_spec(ctx):
    """Virtual machine configuration specification."""
    try:
        cli_manager = ctx.obj['CLIManager']
        spec = cli_manager.get_vm_spec(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], spec, spec.keys())
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(spec)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('admin',
                        short_help='Administrator')
@click.pass_context
def compute_vm_get_admin(ctx):
    """Virtual machine administrator. Part of the
    VSS metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        admin = cli_manager.get_vm_vss_admin(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], admin,
                                   ['name',
                                    'email',
                                    'phone'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(admin)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('description',
                        short_help='Description (Metadata)')
@click.pass_context
def compute_vm_get_description(ctx):
    """Virtual machine description. Part of the
    VSS metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        description = cli_manager.get_vm_vss_description(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], description,
                                   ['value'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(description)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('client-note',
                        short_help='Client note (Metadata)')
@click.pass_context
def compute_vm_get_client_notes(ctx):
    """Virtual machine client notes. Part of the
    VM metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        notes = cli_manager.get_vm_notes(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], notes,
                                   ['value'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(notes)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('tools',
                        short_help='VMware Tools Status')
@click.pass_context
def compute_vm_get_tools(ctx):
    """Virtual machine VMware Tools status."""
    try:
        cli_manager = ctx.obj['CLIManager']
        tools = cli_manager.get_vm_tools(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], tools,
                                   ['version',
                                    'versionStatus',
                                    'runningStatus'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(tools)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('name',
                        short_help='Logical name')
@click.pass_context
def compute_vm_get_name(ctx):
    """Virtual machine human readable name."""
    try:
        cli_manager = ctx.obj['CLIManager']
        name = cli_manager.get_vm_name(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], name, ['name'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(name)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('cpu',
                        short_help='CPU configuration')
@click.pass_context
def compute_vm_get_cpu(ctx):
    """Virtual machine cpu configuration.
    Get CPU count and quick stats."""
    try:
        cli_manager = ctx.obj['CLIManager']
        cpu = cli_manager.get_vm_cpu(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], cpu,
                                   ['cpu', 'coresPerSocket',
                                    ('hotAdd', 'enabled'),
                                    ('hotRemove', 'enabled')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(cpu)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('nic',
                        short_help='NIC configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_nics(ctx, unit):
    """Virtual machine network interface adapters configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            nic = cli_manager.get_vm_nic(ctx.obj['UUID'], unit)
            if not cli_manager.output_json:
                _lines = print_vm_attr(ctx.obj['UUID'], nic[0],
                                       ['label',
                                        'type',
                                        'connected',
                                        'startConnected',
                                        'macAddress',
                                        ('network', 'name'),
                                        ('network', 'moref')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(nic)
        else:
            nics = cli_manager.get_vm_nics(ctx.obj['UUID'])
            nics = [n.get('data') for n in nics]
            if not cli_manager.output_json:
                _lines = print_vm_objects_attr(ctx.obj['UUID'], nics,
                                               ['label', 'macAddress'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(nics)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('floppy',
                        short_help='Floppy configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_floppies(ctx, unit):
    """Virtual machine Floppy configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            dev = cli_manager.get_vm_floppy(ctx.obj['UUID'], unit)
            if cli_manager.output not in ['json']:
                _lines = print_vm_attr(ctx.obj['UUID'], dev[0],
                                       ['label', 'backing',
                                        'connected',
                                        ('controller', 'type'),
                                        ('controller', 'virtualDeviceNode')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(dev)
        else:
            devs = cli_manager.get_vm_floppies(ctx.obj['UUID'])
            devs = [d.get('data') for d in devs]
            if cli_manager.output not in ['json']:
                _lines = print_vm_objects_attr(ctx.obj['UUID'], devs,
                                               ['label', 'backing'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(devs)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('cd',
                        short_help='CD/DVD configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_cds(ctx, unit):
    """Virtual machine CD/DVD configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            cd = cli_manager.get_vm_cd(ctx.obj['UUID'], unit)
            if cli_manager.output not in ['json']:
                _lines = print_vm_attr(ctx.obj['UUID'], cd[0],
                                       ['label', 'backing',
                                        'connected',
                                        ('controller', 'type'),
                                        ('controller', 'virtualDeviceNode')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(cd)
        else:
            devs = cli_manager.get_vm_cds(ctx.obj['UUID'])
            devs = [d.get('data') for d in devs]
            if cli_manager.output not in ['json']:
                _lines = print_vm_objects_attr(ctx.obj['UUID'], devs,
                                               ['label', 'backing'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(devs)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('disk',
                        short_help='Disk configuration')
@click.argument('unit', type=int, required=False)
@click.pass_context
def compute_vm_get_disks(ctx, unit):
    """Virtual machine Disk configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if unit:
            disk = cli_manager.get_vm_disk(ctx.obj['UUID'], unit)
            if not cli_manager.output_json:
                _lines = print_vm_attr(ctx.obj['UUID'], disk[0],
                                       ['label', 'capacityGB',
                                        'provisioning',
                                        ('controller', 'type'),
                                        ('controller', 'virtualDeviceNode'),
                                        ('shares', 'level')])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(disk)
        else:
            disks = cli_manager.get_vm_disks(ctx.obj['UUID'])
            disks = [d.get('data') for d in disks]
            if not cli_manager.output_json:
                _lines = print_vm_objects_attr(ctx.obj['UUID'], disks,
                                               ['label', 'capacityGB'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(disks)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('alarm',
                        short_help='Triggered alarms')
@click.argument('alarm_moref', type=str, required=False)
@click.pass_context
def compute_vm_get_alarms(ctx, alarm_moref):
    """Virtual machine triggered alarms."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if alarm_moref:
            alarm = cli_manager.get_vm_alarm(ctx.obj['UUID'], alarm_moref)
            if not cli_manager.output_json:
                _lines = print_vm_attr(ctx.obj['UUID'], alarm[0],
                                       ['name',
                                        'overallStatus',
                                        'acknowledged',
                                        'acknowledgedDateTime',
                                        'dateTime',
                                        'acknowledgedByUser'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(alarm)
        else:
            objs = cli_manager.get_vm_alarms(ctx.obj['UUID'])
            if not cli_manager.output_json:
                _lines = print_vm_objects_attr(ctx.obj['UUID'], objs,
                                               ['moref', 'name',
                                                'overallStatus',
                                                'dateTime'])
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(objs)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('memory',
                        short_help='Memory configuration')
@click.pass_context
def compute_vm_get_memory(ctx):
    """Virtual machine memory configuration."""
    try:
        cli_manager = ctx.obj['CLIManager']
        mem = cli_manager.get_vm_memory(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], mem,
                                   ['memoryGB',
                                    ('hotAdd', 'enabled'),
                                    ('hotAdd', 'limitGB')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(mem)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('template',
                        short_help='Template configuration')
@click.pass_context
def compute_vm_get_template(ctx):
    """Virtual machine template state."""
    try:
        cli_manager = ctx.obj['CLIManager']
        template = cli_manager.is_vm_template(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], template,
                                   ['isTemplate'])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(template)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('state',
                        short_help='State')
@click.pass_context
def compute_vm_get_state(ctx):
    """Virtual machine running and power state."""
    try:
        cli_manager = ctx.obj['CLIManager']
        state = cli_manager.get_vm_state(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], state,
                                   ['connectionState', 'powerState',
                                    'bootTime', ('domain', 'name')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(state)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('domain',
                        short_help='Running domain')
@click.pass_context
def compute_vm_get_domain(ctx):
    """Virtual machine running domain"""
    try:
        cli_manager = ctx.obj['CLIManager']
        domain = cli_manager.get_vm_domain(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], domain,
                                   [('domain', 'moref'),
                                    ('domain', 'name')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(domain)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('folder',
                        short_help='Logical folder')
@click.pass_context
def compute_vm_get_folder(ctx):
    """Virtual machine logical folder."""
    try:
        cli_manager = ctx.obj['CLIManager']
        folder = cli_manager.get_vm_folder(ctx.obj['UUID'])
        if not cli_manager.output_json:
            _lines = print_vm_attr(ctx.obj['UUID'], folder,
                                   ['path', 'name', 'parent',
                                    ('folder', 'moref')])
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(folder)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('console',
                        short_help='HTML console link')
@click.option('-l', '--launch', is_flag=True,
              help='Launch link in default browser')
@click.pass_context
def compute_vm_get_console(ctx, launch):
    """'Get one-time HTML link to access console"""
    try:
        cli_manager = ctx.obj['CLIManager']
        console = cli_manager.get_vm_console(ctx.obj['UUID'])
        link = console.get('value')
        if not cli_manager.output_json:
            lines = columns_two_kv.format('Link', link)
        else:
            lines = pretty_print(console)
        click.echo(lines)
        if launch:
            click.launch(link)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('version',
                        short_help='Hardware (VMX) version')
@click.pass_context
def compute_vm_get_version(ctx):
    """Get VMX hardware version"""
    try:
        cli_manager = ctx.obj['CLIManager']
        version = cli_manager.get_vm_version(ctx.obj['UUID'])
        if not cli_manager.output_json:
            lines = columns_two_kv.format('Version',
                                          version.get('value'))
        else:
            lines = pretty_print(version)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_get.command('event',
                        short_help='Events')
@click.option('-w', '--window', type=int, default=1,
              help='Launch link in default browser')
@click.pass_context
def compute_vm_get_events(ctx, window):
    """Get virtual machine related events in given time window"""
    try:
        cli_manager = ctx.obj['CLIManager']
        events = cli_manager.get_vm_events(ctx.obj['UUID'], window)
        if cli_manager.output_json:
            _lines = pretty_print(events)
            lines = '\n'.join(_lines)
        else:
            _lines = print_vm_objects_attr(ctx.obj['UUID'], events['events'],
                                           ['userName', 'createdTime',
                                            'message'])
            lines = '\n'.join(_lines)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('rm', help='Delete given virtual machine',
                  invoke_without_command=True)
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force deletion if power state is on')
@click.option('-m', '--max-del', type=click.IntRange(1, 10),
              required=False, default=3)
@click.argument('uuid', type=click.UUID, required=True, nargs=-1)
@click.pass_context
def compute_vm_rm(ctx, uuid, force, max_del):
    try:
        requests = list()
        cli_manager = ctx.obj['CLIManager']
        if len(uuid) > max_del:
            raise click.UsageError('Increase max instance removal with '
                                   '--max-del/-m option')
        for vm in uuid:
            requests.append(cli_manager.delete_vm(uuid=vm,
                                                  force=force))
        for request in requests:
            if not cli_manager.output_json:
                lines = '\n'.join(print_request(request))
            else:
                lines = pretty_print(request)
            click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('mk', help='Create virtual machine',
                  invoke_without_command=False)
@click.pass_context
def compute_vm_create(ctx):
    """"""
    pass


@compute_vm_create.command('shell',
                           short_help='Create empty virtual machine')
@click.argument('name', type=str, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=True)
@click.option('--admin', '-a', help='Admin name, phone number and '
                                    'email separated by `:` i.e. '
                                    '"John Doe:416-123-1234:'
                                    'john.doe@utoronto.ca"',
              type=str, callback=validate_admin, required=False)
@click.option('--inform', '-r', help='Informational contact emails in'
                                     ' comma separated',
              type=str, callback=validate_inform, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=True)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False, default=1)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False, default=1)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=True)
@click.option('--disk', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False,
              default=[40])
@click.option('--net', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=True)
@click.option('--iso', '-s',
              help='ISO image path to be mounted after creation',
              type=str, required=False)
@click.option('--domain', '-t', help='Target fault domain.',
              type=str, required=False)
@click.option('--high-io', '-h', help='VM will be created with '
                                      'a VMware Paravirtual '
                                      'SCSIController.',
              is_flag=True, required=False)
@click.option('--notes', '-t', help='Custom notes.',
              type=str, required=False)
@click.pass_context
def compute_vm_create_shell(ctx, name, description, bill_dept,
                            usage, os, memory, cpu, folder, disk,
                            net, domain, high_io, iso, notes, admin,
                            inform):
    """Create a new virtual machine with no operating system pre-installed."""
    try:
        built = 'os_install'
        cli_manager = ctx.obj['CLIManager']
        name = name
        new_vm_spec = dict(description=description, name=name,
                           usage=usage, built=built, high_io=high_io)
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        if os:
            new_vm_spec['os'] = os
        if memory:
            new_vm_spec['memory'] = memory
        if cpu:
            new_vm_spec['cpu'] = cpu
        if folder:
            new_vm_spec['folder'] = folder
        if net:
            new_vm_spec['networks'] = list(net)
        if disk:
            new_vm_spec['disks'] = list(disk)
        if domain:
            new_vm_spec['domain'] = domain
        if iso:
            new_vm_spec['iso'] = iso
        if notes:
            new_vm_spec['notes'] = notes
        if admin:
            name, phone, email = admin.split(':')
            new_vm_spec['admin_email'] = email
            new_vm_spec['admin_phone'] = phone
            new_vm_spec['admin_name'] = name
        if inform:
            new_vm_spec['inform'] = inform
        # updating spec with new vm spec
        request = cli_manager.create_vm(**new_vm_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from-spec',
                           short_help='Create vm from another vm spec')
@click.argument('name', type=str, required=True)
@click.option('--source', '-s', help='Source VM.',
              type=click.UUID, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=False)
@click.option('--admin', '-a', help='Admin name, phone number and '
                                    'email separated by `:` i.e. '
                                    '"John Doe:416-123-1234:'
                                    'john.doe@utoronto.ca"',
              type=str, callback=validate_admin, required=False)
@click.option('--inform', '-r', help='Informational contact emails in'
                                     ' comma separated',
              type=str, callback=validate_inform, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=False)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=False)
@click.option('--disk', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False)
@click.option('--net', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=False)
@click.option('--domain', '-t', help='Target fault domain.',
              type=str, required=False)
@click.option('--notes', '-t', help='Custom notes.',
              type=str, required=False)
@click.pass_context
def compute_vm_create_spec(ctx, name, source, description, bill_dept, usage,
                           os, memory, cpu, folder, disk, net, domain,
                           notes, admin, inform):
    """Create virtual machine based on another virtual machine configuration
    specification."""
    try:
        built = 'os_install'
        cli_manager = ctx.obj['CLIManager']
        name = name
        source_spec = cli_manager.get_vm_spec(source)
        new_vm_spec = dict(description=description, name=name,
                           usage=usage, built=built)
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        if os:
            new_vm_spec['os'] = os
        if memory:
            new_vm_spec['memory'] = memory
        if cpu:
            new_vm_spec['cpu'] = cpu
        if folder:
            new_vm_spec['folder'] = folder
        if net:
            new_vm_spec['networks'] = list(net)
        if disk:
            new_vm_spec['disks'] = list(disk)
        if notes:
            new_vm_spec['notes'] = notes
        if admin:
            name, phone, email = admin.split(':')
            new_vm_spec['admin_email'] = email
            new_vm_spec['admin_phone'] = phone
            new_vm_spec['admin_name'] = name
        if inform:
            new_vm_spec['inform'] = inform
        if domain:
            new_vm_spec['domain'] = domain
        else:
            source_spec.pop('domain', None)
        # updating spec with new vm spec
        source_spec.update(new_vm_spec)
        request = cli_manager.create_vm(**source_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from-template',
                           short_help='Create vm from template.')
@click.argument('name', type=str, required=True)
@click.option('--source', '-s', help='Source vm template.',
              type=click.UUID, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=False)
@click.option('--admin', '-a', help='Admin name, phone number and '
                                    'email separated by `:` i.e. '
                                    '"John Doe:416-123-1234:'
                                    'john.doe@utoronto.ca"',
              type=str, callback=validate_admin, required=False)
@click.option('--inform', '-r', help='Informational contact emails in'
                                     ' comma separated',
              type=str, callback=validate_inform, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=False)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=False)
@click.option('--disk', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False)
@click.option('--net', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=False)
@click.option('--domain', '-t', help='Target fault domain.',
              type=str, required=False)
@click.option('--custom-spec', '-p',
              help='Guest OS custom specification in JSON format.',
              type=str, required=False,
              callback=validate_json_type)
@click.option('--notes', '-t', help='Custom notes.',
              type=str, required=False)
@click.pass_context
def compute_vm_create_template(ctx, name, source, description, bill_dept,
                               usage, os, memory, cpu, folder, disk,
                               net, custom_spec, domain, notes, admin,
                               inform):
    """Deploy virtual machine from template"""
    try:
        cli_manager = ctx.obj['CLIManager']
        # validate template
        new_vm_spec = dict(description=description, name=name,
                           usage=usage,
                           source_template=str(source))
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        if os:
            new_vm_spec['os'] = os
        if memory:
            new_vm_spec['memoryGB'] = memory
        if cpu:
            new_vm_spec['cpu'] = cpu
        if folder:
            new_vm_spec['folder'] = folder
        if net:
            new_vm_spec['networks'] = list(net)
        if disk:
            new_vm_spec['disks'] = list(disk)
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        if notes:
            new_vm_spec['notes'] = notes
        if admin:
            name, phone, email = admin.split(':')
            new_vm_spec['admin_email'] = email
            new_vm_spec['admin_phone'] = phone
            new_vm_spec['admin_name'] = name
        if inform:
            new_vm_spec['inform'] = inform
        if domain:
            new_vm_spec['domain'] = domain
        # submitting request
        request = cli_manager.deploy_vm_from_template(**new_vm_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from-image',
                           short_help='Create vm from OVA/OVF image.')
@click.argument('name', type=str, required=True)
@click.option('--image', '-a', help='Source Virtual Machine OVA/OVF.',
              type=str, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=True)
@click.option('--admin', '-a', help='Admin name, phone number and '
                                    'email separated by `:` i.e. '
                                    '"John Doe:416-123-1234:'
                                    'john.doe@utoronto.ca"',
              type=str, callback=validate_admin, required=False)
@click.option('--inform', '-r', help='Informational contact emails in'
                                     ' comma separated',
              type=str, callback=validate_inform, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=True)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=True)
@click.option('--disk', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False)
@click.option('--net', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=True)
@click.option('--domain', '-t', help='Target fault domain.',
              type=str, required=False)
@click.option('--custom-spec', '-p',
              help='Guest OS custom specification in JSON format.',
              type=str, required=False,
              callback=validate_json_type)
@click.option('--extra-config', '-e',
              help='VMWare Guest Info Interface in JSON format.',
              type=str, required=False, callback=validate_json_type)
@click.option('--user-data', '-s', help='Cloud-init user_data YML file path '
                                        'to pre-configure '
                                        'guest os upon first boot.',
              type=click.File('r'),
              required=False)
@click.option('--notes', '-t', help='Custom notes.',
              type=str, required=False)
@click.pass_context
def compute_vm_create_image(ctx, image, name, description, bill_dept,
                            usage, os, memory, cpu, folder, disk,
                            net, custom_spec, domain, extra_config,
                            user_data, notes, admin, inform):
    """Deploy virtual machine from image"""
    try:
        try:
            cli_manager = ctx.obj['CLIManager']
            # validate image
            source_image = image
            cli_manager.get_images(path=source_image)
            new_vm_spec = dict(description=description, name=name,
                               usage=usage,
                               image=str(source_image),
                               os=os, folder=folder,
                               networks=list(net),
                               disks=list(disk))
            if bill_dept:
                new_vm_spec['bill_dept'] = bill_dept
            if memory:
                new_vm_spec['memoryGB'] = memory
            if cpu:
                new_vm_spec['cpu'] = cpu
            if custom_spec:
                new_vm_spec['custom_spec'] = custom_spec
            if domain:
                new_vm_spec['domain'] = domain
            if notes:
                new_vm_spec['notes'] = notes
            if extra_config:
                new_vm_spec['extra_config'] = extra_config
            if user_data:
                new_vm_spec['user_data'] = user_data.read()
            if admin:
                name, phone, email = admin.split(':')
                new_vm_spec['admin_email'] = email
                new_vm_spec['admin_phone'] = phone
                new_vm_spec['admin_name'] = name
            if inform:
                new_vm_spec['inform'] = inform
            # submitting request
            request = cli_manager.create_vm_from_image(**new_vm_spec)
            # print result
            if not cli_manager.output_json:
                _lines = print_request(request)
                lines = '\n'.join(_lines)
            else:
                lines = pretty_print(request)
            click.echo(lines)
        except VssError as ex:
            raise VssCLIError(ex.message)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from-clone',
                           short_help='Clone virtual machine.')
@click.argument('name', type=str, required=False)
@click.option('--source', '-s', help='Source vm.',
              type=click.UUID, required=True)
@click.option('--description', '-d', help='Vm description.',
              type=str, required=True)
@click.option('--bill-dept', '-b', help='Billing department.',
              type=str, required=False)
@click.option('--admin', '-a', help='Admin name, phone number and '
                                    'email separated by `:` i.e. '
                                    '"John Doe:416-123-1234:'
                                    'john.doe@utoronto.ca"',
              type=str, callback=validate_admin, required=False)
@click.option('--inform', '-r', help='Informational contact emails in'
                                     ' comma separated',
              type=str, callback=validate_inform, required=False)
@click.option('--usage', '-u', help='Vm usage.',
              type=click.Choice(['Test', 'Prod', 'Dev', 'QA']),
              required=False, default='Test')
@click.option('--os', '-o', help='Guest operating system id.',
              type=str, required=False)
@click.option('--memory', '-m', help='Memory in GB.',
              type=int, required=False)
@click.option('--cpu', '-c', help='Cpu count.',
              type=int, required=False)
@click.option('--folder', '-f', help='Logical folder moref.',
              type=str, required=False)
@click.option('--disk', '-i', help='Disks in GB.',
              type=int, multiple=True, required=False)
@click.option('--net', '-n', help='Networks moref mapped to NICs.',
              type=str, multiple=True, required=False)
@click.option('--domain', '-t', help='Target fault domain.',
              type=str, required=False)
@click.option('--custom-spec', '-p',
              help='Guest OS custom specification in JSON format.',
              type=str, required=False,
              callback=validate_json_type)
@click.option('--notes', '-t', help='Custom notes.',
              type=str, required=False)
@click.pass_context
def compute_vm_clone(ctx, name, source, description, bill_dept,
                     usage, os, memory, cpu, folder, disk,
                     net, custom_spec, domain, notes, admin, inform):
    """Clone virtual machine from running or powered off vm.
    If name argument is not specified, -clone suffix will be added to
    resulting virtual machine"""
    try:
        cli_manager = ctx.obj['CLIManager']
        new_vm_spec = dict(description=description, name=name,
                           usage=usage,
                           source_vm=str(source))
        if bill_dept:
            new_vm_spec['bill_dept'] = bill_dept
        if os:
            new_vm_spec['os'] = os
        if memory:
            new_vm_spec['memoryGB'] = memory
        if cpu:
            new_vm_spec['cpu'] = cpu
        if folder:
            new_vm_spec['folder'] = folder
        if net:
            new_vm_spec['networks'] = list(net)
        if disk:
            new_vm_spec['disks'] = list(disk)
        if custom_spec:
            new_vm_spec['custom_spec'] = custom_spec
        if notes:
            new_vm_spec['notes'] = notes
        if domain:
            new_vm_spec['domain'] = domain
        if admin:
            name, phone, email = admin.split(':')
            new_vm_spec['admin_email'] = email
            new_vm_spec['admin_phone'] = phone
            new_vm_spec['admin_name'] = name
        if inform:
            new_vm_spec['inform'] = inform
        # submitting request
        request = cli_manager.create_vm_from_clone(**new_vm_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_create.command('from-file',
                           short_help='Create virtual machine from '
                                      'file specification.')
@click.argument('file-spec', type=click.File('rb'))
@click.pass_context
def compute_vm_from_file(ctx, file_spec):
    """Create virtual machine from file specification.
    Virtual Machine specification can be obtained from

    vss compute vm get <uuid> spec > spec.json

    """
    cli_manager = ctx.obj['CLIManager']
    try:
        import json
        new_vm_spec = json.load(file_spec)
        new_vm_spec['built'] = new_vm_spec['built_from']
        request = cli_manager.create_vm(**new_vm_spec)
        # print result
        if not cli_manager.output_json:
            _lines = print_request(request)
            lines = '\n'.join(_lines)
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm.group('set',
                  short_help='Set given vm attribute.',
                  invoke_without_command=True)
@click.argument('uuid', type=click.UUID, required=True)
@click.option('-s', '--schedule', type=str, required=False,
              help='Schedule change in a given point in time based on'
                   'format YYYY-MM-DD HH:MM.',
              callback=validate_schedule)
@click.pass_context
def compute_vm_set(ctx, uuid, schedule):
    """Set given virtual machine attribute such as cpu,
    memory, disk, network backing, cd, etc."""
    if ctx.invoked_subcommand is None:
        raise click.UsageError('Sub command is required.')
    try:
        ctx.obj['UUID'] = str(uuid)
        if schedule:
            ctx.obj['SCHEDULE'] = schedule
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('alarm',
                        short_help='Acknowledge or clear alarms')
@click.argument('alarm_moref', type=str, required=True)
@click.option('-a', '--action', type=click.Choice(['ack', 'cl']),
              help='Action to perform', required=True)
@click.pass_context
def compute_vm_set_alarm(ctx, action, alarm_moref):
    """Acknowledge or clear a given alarm. Obtain alarm moref by:

        vss compute vm get <uuid> alarm

    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       moref=alarm_moref)
        # alarm exist?
        cli_manager.get_vm_alarm(**payload)
        # schedule?
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        # action
        if action == 'ack':
            request = cli_manager.ack_vm_alarm(**payload)
        else:
            request = cli_manager.clear_vm_alarm(**payload)

        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('snapshot',
                        short_help='Create, delete, revert snapshot')
@click.option('-i', '--snapshot-id', type=int, required=False,
              help='Snapshot Id to delete or revert')
@click.option('-a', '--action', type=click.Choice(['mk', 'rm', 're']),
              help='Action to perform', required=True)
@click.option('-d', '--description', type=str,
              help='A brief description of the snapshot.')
@click.option('-t', '--timestamp', type=str, callback=validate_schedule,
              help='Timestamp to create the snapshot from.')
@click.option('-l', '--lifetime', type=click.IntRange(1, 72),
              help='Number of hours the snapshot will live.')
@click.pass_context
def compute_vm_set_snapshot(ctx, action, snapshot_id, description,
                            timestamp, lifetime):
    """Creates, deletes and reverts a Virtual Machine snapshot
    on a given date and time."""
    try:
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            click.echo('Warning: Schedule is ignored for snapshots.',
                       color='orange')
        uuid = ctx.obj['UUID']
        # action
        if action in ['rm', 're'] and not snapshot_id:
            raise click.UsageError('-i/--snapshot-id is required')
        if action in ['mk'] and not (description and timestamp and lifetime):
            raise click.UsageError('-d/--description, -t/--timestamp and '
                                   '-l/--lifetime are required to create a '
                                   'snapshot.')
        lookup = {'mk': (cli_manager.create_vm_snapshot,
                         dict(uuid=uuid,
                              desc=description,
                              date_time=timestamp,
                              valid=lifetime)),
                  'rm': (cli_manager.delete_vm_snapshot,
                         dict(uuid=uuid,
                              snapshot=snapshot_id)),
                  're': (cli_manager.revert_vm_snapshot,
                         dict(uuid=uuid,
                              snapshot=snapshot_id))}
        try:
            f, payload = lookup[action]
            request = f(**payload)
        except KeyError:
            raise click.BadOptionUsage('Invalid action')
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('version',
                        short_help='Hardware (VMX) version')
@click.option('-o', '--on', type=click.Choice(['boot', 'now']),
              default='boot',
              help='Perform upgrade now or on next boot')
@click.pass_context
def compute_vm_set_version(ctx, on):
    """Upgrade vm hardware (vmx) to latest version either on
    next boot or now."""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       parameter='upgrade',
                       value=on)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.upgrade_vm_version(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('folder',
                        short_help='Logical folder')
@click.argument('moref', type=str, required=True)
@click.pass_context
def compute_vm_set_folder(ctx, moref):
    """Move vm from logical folder. Get folder moref from:

        vss compute folder ls

    """
    try:
        cli_manager = ctx.obj['CLIManager']
        # check if folder exists or is accessible
        cli_manager.get_folder(moref)
        payload = dict(uuid=ctx.obj['UUID'],
                       folder_moId=moref)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_folder(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.group('disk',
                      short_help='Virtual disk settings')
@click.pass_context
def compute_vm_set_disk(ctx):
    """Manage virtual machine disks. Add, expand and remove virtual disks."""
    pass


@compute_vm_set_disk.command('mk',
                             short_help='Create new disk')
@click.option('-c', '--capacity', type=int,
              required=True,
              help='Update given disk capacity in GB.')
@click.pass_context
def compute_vm_set_disk_mk(ctx, capacity):
    """Create virtual machine disk:

        vss compute vm set <uuid> disk mk --capacity 10
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        # crafting payload
        payload['valueGB'] = capacity
        request = cli_manager.create_vm_disk(**payload)
        # print result
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set_disk.command('up',
                             short_help='Update disk capacity')
@click.argument('unit', type=int, required=True)
@click.option('-c', '--capacity', type=int,
              required=True,
              help='Update given disk capacity in GB.')
@click.pass_context
def compute_vm_set_disk_up(ctx, unit, capacity):
    """Update virtual machine disk capacity:

        vss compute vm set <uuid> disk up --capacity 30 <unit>
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        # crafting payload
        payload['disk'] = unit
        payload['valueGB'] = capacity
        request = cli_manager.update_vm_disk_capacity(**payload)
        # print result
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set_disk.command('rm',
                             short_help='Remove disk from vm')
@click.argument('unit', type=int, required=True)
@click.option('-r', '--rm', is_flag=True, default=False,
              help='Confirm disk removal')
@click.pass_context
def compute_vm_set_disk_rm(ctx, unit, rm):
    """Remove virtual machine disk. Warning: data will be lost:

        vss compute vm set <uuid> disk rm <unit>
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        payload['disk'] = unit
        confirm = rm or click.confirm('Are you sure you want to '
                                      'delete disk unit {0}?'.format(unit))
        if confirm:
            request = cli_manager.delete_vm_disk(**payload)
        else:
            raise click.ClickException('Cancelled by user.')
        # print result
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.group('nic',
                      short_help='Virtual nic settings.')
@click.pass_context
def compute_vm_set_nic(ctx):
    """Add, remove or update virtual machine network adapters

        vss compute vm set <uuid> nic mk --network <net-moref>

    """
    pass


@compute_vm_set_nic.command('up',
                            short_help='Update NIC unit')
@click.argument('unit', type=int, required=True)
@click.option('-n', '--network', type=str,
              help='Virtual network moref')
@click.option('-s', '--state', type=click.Choice(['connect',
                                                  'disconnect']),
              help='Updates nic state')
@click.option('-t', '--type', type=click.Choice(['VMXNET2', 'VMXNET3',
                                                 'E1000', 'E1000e']),
              help='Updates nic type')
@click.pass_context
def compute_vm_set_nic_up(ctx, unit, network, state, type):
    """Update network adapter backing network, type or state

        vss compute vm set <uuid> nic up --type VMXNET3 <unit>
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       nic=unit)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')

        lookup = {'network': cli_manager.update_vm_nic_network,
                  'state': cli_manager.update_vm_nic_state,
                  'type': cli_manager.update_vm_nic_type}
        # select option
        if network:
            attr = 'network'
            _ = cli_manager.get_network(network)
            value = network
        elif state:
            attr = 'state'
            value = state
        elif type:
            attr = 'type'
            value = type
        else:
            raise click.UsageError('Select at least one '
                                   'setting to change')
        # submitting request
        f = lookup[attr]
        payload[attr] = value
        request = f(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set_nic.command('mk',
                            short_help='Create NIC unit')
@click.option('-n', '--network', type=str,
              help='Virtual network moref')
@click.pass_context
def compute_vm_set_nic_mk(ctx, network):
    """Add network adapter specifying backing network.

        vss compute vm set <uuid> nic mk --network <net-moref>
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        # validate network
        _ = cli_manager.get_network(network)
        payload['network'] = network
        # submit request
        request = cli_manager.create_vm_nic(**payload)
        # print request
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set_nic.command('rm',
                            short_help='Remove NIC unit')
@click.argument('unit', type=int, required=True)
@click.option('-r', '--rm', is_flag=True, default=False,
              help='Confirm nic removal')
@click.pass_context
def compute_vm_set_nic_rm(ctx, unit, rm):
    """Remove given network adapter

        vss compute vm set <uuid> nic rm <unit>
    """
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       nic=unit)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        confirm = rm or click.confirm('Are you sure you want to '
                                      'delete nic unit {0}?'.format(unit))
        if confirm:
            request = cli_manager.delete_vm_nic(**payload)
        else:
            raise click.ClickException('Cancelled by user.')
        # print request
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('floppy',
                        short_help='Floppy backing')
@click.argument('unit', type=int, required=True)
@click.option('-i', '--image', type=str, required=False,
              help='Update floppy backing device to'
                   ' given flp image path.')
@click.option('-c', '--client', is_flag=True, required=False,
              help='Update floppy backing device to client device.')
@click.pass_context
def compute_vm_set_floppy(ctx, unit, image, client):
    """Update virtual machine floppy backend to Image or client"""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       unit=unit, image=image or not client)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_floppy(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('cd',
                        short_help='CD/DVD backing')
@click.argument('unit', type=int, required=True)
@click.option('-i', '--iso', type=str, required=False,
              help='Update CD/DVD backing device to given ISO path.')
@click.option('-c', '--client', is_flag=True, required=False,
              help='Update CD/DVD backing device to client device.')
@click.pass_context
def compute_vm_set_cd(ctx, unit, iso, client):
    """Update virtual machine CD/DVD backend to ISO or client"""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       cd=unit, iso=iso or not client)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_cd(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('usage',
                        short_help='Usage (Metadata)')
@click.argument('usage', type=click.Choice(['Prod', 'Test',
                                            'Dev', 'QA']),
                required=True)
@click.pass_context
def compute_vm_set_usage(ctx, usage):
    """Update virtual machine usage in both name prefix
    and metadata"""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       usage=usage)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_usage(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('client',
                        short_help='Client (Metadata)')
@click.argument('state', type=str,
                required=True)
@click.pass_context
def compute_vm_set_client(ctx, usage):
    """Update virtual machine client/billing department"""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict(uuid=ctx.obj['UUID'],
                       usage=usage)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_client(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('boot',
                        short_help='Boot configuration')
@click.option('-c', '--bios', is_flag=True,
              required=False,
              help='Next boot enter to BIOS.')
@click.option('-d', '--delay', type=int,
              required=False,
              help='Boot delay in milliseconds.')
@click.pass_context
def compute_vm_set_bios(ctx, bios, delay):
    """Update virtual machine boot configuration. Boot directly to BIOS or
    set a new boot delay in milliseconds."""
    try:
        cli_manager = ctx.obj['CLIManager']
        payload = dict()
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        if bios:
            payload['boot_bios'] = bios
            request = cli_manager.update_vm_boot_bios(**payload)
        else:
            payload['boot_delay'] = delay
            request = cli_manager.update_vm_boot_delay(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('ha-group',
                        help='HA Group (Metadata)')
@click.argument('uuid', type=click.UUID, nargs=-1, required=True)
@click.option('-r', '--replace', is_flag=True,
              required=False,
              help='Replace existing value.')
@click.pass_context
def compute_vm_set_ha_group(ctx, uuid, replace):
    """Create HA group by tagging virtual machines with given Uuids.
    Checks will run every hour to validate virtual machine association
    and domain separation."""
    try:
        cli_manager = ctx.obj['CLIManager']
        for v in uuid:
            cli_manager.get_vm(v)
        append = not replace
        payload = dict(append=append,
                       vms=list(uuid),
                       uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_ha_group(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('consolidate',
                        short_help='Disk consolidation')
@click.pass_context
def compute_vm_set_consolidate(ctx):
    """Perform virtual machine disk consolidation"""
    try:
        payload = dict(uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.consolidate_vm_disks(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('inform',
                        short_help='Informational contacts (Metadata)')
@click.argument('email', type=str, nargs=-1, required=True)
@click.option('-r', '--replace', is_flag=True,
              required=False,
              help='Replace existing value.')
@click.pass_context
def compute_vm_set_inform(ctx, email, replace):
    """Update or set informational contacts emails in
    metadata."""
    try:
        for e in email:
            validate_email(ctx, '', e)
        append = not replace
        payload = dict(append=append,
                       emails=list(email),
                       uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_inform(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('admin',
                        short_help='Administrator')
@click.argument('name', type=str, required=True)
@click.argument('email', type=str, required=True)
@click.argument('phone', type=str, required=True)
@click.pass_context
def compute_vm_set_admin(ctx, name, email, phone):
    """Set or update virtual machine administrator in metadata."""
    try:
        payload = dict(name=name,
                       phone=phone,
                       email=email,
                       uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        validate_phone_number(ctx, '', phone)
        validate_email(ctx, '', email)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_admin(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('description',
                        short_help='Description (Metadata)')
@click.argument('description',
                required=True)
@click.pass_context
def compute_vm_set_description(ctx, description):
    """Set or update virtual machine description in metadata."""
    try:
        payload = dict(description=description,
                       uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_vss_description(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('client-note',
                        short_help='Client note (Metadata)')
@click.argument('notes',
                required=True)
@click.option('--replace', '-r', is_flag=True, required=False,
              help="Whether to replace existing value.")
@click.pass_context
def compute_vm_set_client_note(ctx, notes, replace):
    """Set or update virtual machine client notes
     in metadata."""
    try:
        cli_manager = ctx.obj['CLIManager']
        uuid = ctx.obj['UUID']
        if not replace:
            try:
                _old_notes = cli_manager.get_vm_notes(uuid)
            except VssError:
                _old_notes = dict()
            old_notes = _old_notes.get('value') or ""
            notes = "{}\n{}".format(old_notes, notes)
        # creating payload
        payload = dict(notes=notes,
                       uuid=ctx.obj['UUID'])
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_notes(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('tools',
                        short_help='Manage VMware Tools')
@click.argument('action', type=click.Choice(['upgrade',
                                             'mount',
                                             'unmount']), required=True)
@click.pass_context
def compute_vm_set_tools(ctx, action):
    """Upgrade, mount and unmount official VMware Tools package.
    This command does not apply for Open-VM-Tools."""
    try:
        payload = dict(action=action, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_tools(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('name',
                        short_help='Logical name')
@click.argument('name', type=str, required=True)
@click.pass_context
def compute_vm_set_name(ctx, name):
    """Update virtual machine name only. It does not update
    VSS prefix YYMM{P|D|Q|T}."""
    try:
        payload = dict(name=name, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.rename_vm(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('cpu',
                        short_help='CPU count')
@click.argument('cpu_count', type=int, required=True)
@click.pass_context
def compute_vm_set_cpu(ctx, cpu_count):
    """Update virtual machine CPU count."""
    try:
        payload = dict(number=cpu_count, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.set_vm_cpu(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('memory',
                        short_help='Memory in GB')
@click.argument('memory', type=int, required=True)
@click.pass_context
def compute_vm_set_memory(ctx, memory):
    """Update virtual machine memory size in GB."""
    try:
        payload = dict(sizeGB=memory, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.set_vm_memory(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('state',
                        short_help='Power state')
@click.argument('state', type=click.Choice(['on', 'off', 'restart',
                                           'reset', 'shutdown']),
                required=True)
@click.pass_context
def compute_vm_set_state(ctx, state):
    """ Set given virtual machine power state.
    On will power on virtual machine. Off power offs virtual machine.
    Reset power cycles virtual machine. Restart sends a guest os
    restart signal (VMWare Tools required). Shutdown sends
    guest os shutdown signal (VMware Tools required).

    """
    try:
        payload = dict(uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        lookup = {'on': cli_manager.power_on_vm,
                  'off': cli_manager.power_off_vm,
                  'reset': cli_manager.reset_vm,
                  'restart': cli_manager.reboot_vm,
                  'shutdown': cli_manager.shutdown_vm}
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = lookup[state](**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('domain',
                        short_help='Domain migration')
@click.argument('domain_moref', type=str,
                required=True)
@click.option('-f', '--force', is_flag=True,
              help='Shut down or power off before migration.')
@click.option('-o', '--on', is_flag=True,
              help='Power of after migrating')
@click.pass_context
def compute_vm_set_domain(ctx, domain_moref, force, on):
    """Migrate a virtual machine to another fault domain.
    In order to proceed with the virtual machine relocation,
    it's required to be in a powered off state. The `force` flag
    will send a shutdown signal anf if times out, will perform a
    power off task. After migration completes, the `on` flag
    indicates to power on the virtual machine."""
    try:
        payload = dict(uuid=ctx.obj['UUID'],
                       poweron=on, force=force)
        cli_manager = ctx.obj['CLIManager']
        # validate domain existence
        cli_manager.get_domain(domain_moref)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.update_vm_domain(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('template',
                        short_help='Mark vm as template or vice versa.')
@click.option('--on/--off', is_flag=True, help='Marks vm as '
                                               'template or template as vm',
              default=False)
@click.pass_context
def compute_vm_set_template(ctx, on):
    """Marks virtual machine as template or template to virtual machine."""
    try:
        payload = dict(value=on, uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        # request
        request = cli_manager.mark_vm_as_template(**payload) \
            if on else cli_manager.mark_template_as_vm(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('export',
                        short_help='Export to OVF')
@click.pass_context
def compute_vm_set_export(ctx):
    """Export current virtual machine to OVF."""
    try:
        payload = dict(uuid=ctx.obj['UUID'])
        cli_manager = ctx.obj['CLIManager']
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        request = cli_manager.export_vm(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


@compute_vm_set.command('custom-spec',
                        short_help='Custom specification')
@click.option('--hostname', '-h', type=str, required=True,
              help='OS hostname.')
@click.option('--domain', '-m', type=str, required=True,
              help='OS domain.')
@click.option('--dns', '-n', type=str, multiple=True,
              required=False, help='DNS list.')
@click.option('--interface', '-i', type=str, required=False,
              multiple=True,
              help='Interfaces to customize in json format.')
@click.pass_context
def compute_vm_set_custom_spec(ctx, hostname, domain,
                               dns, interface):
    """Set up Guest OS customization specification. Virtual machine
    power state require is powered off."""
    try:
        cli_manager = ctx.obj['CLIManager']
        # vm must be powered off
        if cli_manager.is_powered_on_vm(ctx.obj['UUID']):
            raise VssError('Cannot perform operation in current power state')
        # temp custom_spec
        _custom_spec = dict(hostname=hostname, domain=domain)
        if dns:
            _custom_spec['dns'] = dns
        ifaces = list()
        import json
        for _interface in interface:
            validate_json_type(ctx, '', _interface)
            _if = json.loads(_interface)
            ifaces.append(cli_manager.get_custom_spec_interface(**_if))
        # update custom spec with interfaces
        _custom_spec.update({'interfaces': ifaces})
        # create custom_spec
        custom_spec = cli_manager.get_custom_spec(**_custom_spec)
        # create payload
        payload = dict(uuid=ctx.obj['UUID'], custom_spec=custom_spec)
        if ctx.obj.get('SCHEDULE'):
            payload['schedule'] = ctx.obj.get('SCHEDULE')
        # submit custom_spec
        request = cli_manager.create_vm_custom_spec(**payload)
        if not cli_manager.output_json:
            lines = '\n'.join(print_request(request))
        else:
            lines = pretty_print(request)
        click.echo(lines)
    except VssError as ex:
        raise VssCLIError(ex.message)


def cli():
    main_cli(obj={})


if __name__ == '__main__':
    main_cli(obj={})
