#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import re
from os.path import expanduser
import click
import subprocess
import sys
import shutil
from pkg_resources import resource_filename
from configobj import ConfigObj
import jinja2
from prettytable import PrettyTable
from odooast import odooast
from lxml import etree
from operator import itemgetter
from dyools import Operator
from tree_format import format_tree
from dyools import Logger

__VERSION__ = '0.5.0'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''

ODOO = 'odoo'
MANIFEST_FILE = '__manifest__.py'

Log = Logger()


def ___set_odoo():
    global ODOO
    global MANIFEST_FILE
    ODOO = 'odoo'
    MANIFEST_FILE = '__manifest__.py'


def ___set_openerp():
    global ODOO
    global MANIFEST_FILE
    ODOO = 'openerp'
    MANIFEST_FILE = '__openerp__.py'


OPENERP_FILE = '__openerp__.py'
INIT_FILE = '__init__.py'
ADDON_README_FILE = 'README.rst'
PROJECT_README_FILE = 'README.md'
DESCRIPTION = 'description'

MANIFEST_TEMPLATE_FILE = '__manifest__.py'
ADDON_README_TEMPLATE_FILE = 'addon_readme.rst'
PROJECT_README_TEMPLATE_FILE = 'project_readme.md'
ADDON_TEMPLATES_TEMPLATE_FILE = 'templates.xml'

MODELS, VIEWS, WIZARD, CONTROLLERS, SECURITY, DATA, I18N, TESTS, REPORT = 'models', 'views', 'wizard', 'controllers', 'security', 'data', 'i18n', 'tests', 'report'
STATIC, SRC, JS, CSS, XML = 'static', 'src', 'js', 'css', 'xml'
SECURITY_FILE = 'ir.model.access.csv'
CONTROLLER_MAIN_FILE = 'main.py'

home = expanduser("~")
home = os.path.join(home, '.dyvz')
USERS_FILE = os.path.join(home, 'dyv_users.ini')
ADDONS_FILE = os.path.join(home, 'dyv_addons.ini')
PROJECTS_FILE = os.path.join(home, 'dyv_projects.ini')
ASSETS_FILE = os.path.join(home, 'dyv_assets.ini')
REPOS_FILE = os.path.join(home, 'dyv_repos.ini')
CHEMINS_FILE = os.path.join(home, 'dyv_chemins.ini')


def render(tpl_path, context):
    resource_path = os.path.sep.join(['dyv', tpl_path])
    tpl_path = resource_filename(__name__, resource_path)
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
    ).get_template(filename).render(context)


try:
    os.makedirs(home)
except:
    pass

if not os.path.exists(USERS_FILE):
    with codecs.open(USERS_FILE, mode='w+', encoding='utf-8') as config_file:
        pass

if not os.path.exists(ADDONS_FILE):
    with codecs.open(ADDONS_FILE, mode='w+', encoding='utf-8') as config_file:
        pass

if not os.path.exists(PROJECTS_FILE):
    with codecs.open(PROJECTS_FILE, mode='w+', encoding='utf-8') as config_file:
        pass

if not os.path.exists(ASSETS_FILE):
    with codecs.open(ASSETS_FILE, mode='w+', encoding='utf-8') as config_file:
        pass


def l(tmp_v, tmp_len=30):
    suffix = ' ***' if len(tmp_v) > tmp_len else ''
    return str(tmp_v)[:tmp_len] + suffix if tmp_v else ''


@click.group()
@click.option('--user', '-u', type=click.STRING, help="The user to load")
@click.option('--addon', '-a', type=click.STRING, help="The addon to load")
@click.option('--project', '-p', type=click.STRING, help="The project to load")
@click.option('--odoo-version', '-ov', type=click.INT, default=False, help="The version of Odoo")
@click.option('--no-addon', '-na', type=click.BOOL, default=False, is_flag=True, help="No addon by default")
@click.version_option(__VERSION__, expose_value=False, is_eager=True, help="Show the version")
@click.pass_context
def cli(ctx, user, addon, project, odoo_version, no_addon):
    """CLI for DYV"""
    version = odoo_version
    if version and version <= 8:
        ___set_openerp()
    else:
        ___set_odoo()
    user_keys = ['name', 'email', 'company', 'website']
    addon_keys = ['slug', 'name', 'version', 'summary', 'category', 'description', 'depends', 'icon']
    project_keys = ['name', 'slug', 'description', 'year', 'path']
    asset_keys = ['path', 'rename']
    chemin_keys = ['path']
    repo_keys = ['path', 'branch_8', 'branch_9', 'branch_10', 'branch_11', 'branch_12', 'branch_dev', 'branch_master']
    config_user_obj = ConfigObj(USERS_FILE, encoding='utf-8')
    config_addon_obj = ConfigObj(ADDONS_FILE, encoding='utf-8')
    config_project_obj = ConfigObj(PROJECTS_FILE, encoding='utf-8')
    config_asset_obj = ConfigObj(ASSETS_FILE, encoding='utf-8')
    config_repo_obj = ConfigObj(REPOS_FILE, encoding='utf-8')
    config_chemin_obj = ConfigObj(CHEMINS_FILE, encoding='utf-8')
    ctx.obj['config_user_obj'] = config_user_obj
    ctx.obj['config_addon_obj'] = config_addon_obj
    ctx.obj['config_project_obj'] = config_project_obj
    ctx.obj['config_asset_obj'] = config_asset_obj
    ctx.obj['config_repo_obj'] = config_repo_obj
    ctx.obj['config_chemin_obj'] = config_chemin_obj
    assets = {}
    for asset_section in config_asset_obj.sections:
        assets[asset_section] = {
            'rename': config_asset_obj[asset_section].get('rename', ''),
            'path': config_asset_obj[asset_section].get('path', ''),
        }
    repos = {}
    for repo_section in config_repo_obj.sections:
        repos[repo_section] = {
            'path': unicode(config_repo_obj[repo_section].get('path', '')).strip(),
            'branch_8': unicode(config_repo_obj[repo_section].get('branch_8', '')).strip(),
            'branch_9': unicode(config_repo_obj[repo_section].get('branch_9', '')).strip(),
            'branch_10': unicode(config_repo_obj[repo_section].get('branch_10', '')).strip(),
            'branch_11': unicode(config_repo_obj[repo_section].get('branch_11', '')).strip(),
            'branch_12': unicode(config_repo_obj[repo_section].get('branch_12', '')).strip(),
            'branch_dev': unicode(config_repo_obj[repo_section].get('branch_dev', '')).strip(),
            'branch_master': unicode(config_repo_obj[repo_section].get('branch_master', '')).strip(),
        }
    chemins = {}
    for chemin_section in config_chemin_obj.sections:
        chemins[chemin_section] = {
            'path': config_chemin_obj[chemin_section].get('path', ''),
        }
    ctx.obj['assets'] = assets
    ctx.obj['repos'] = repos
    ctx.obj['chemins'] = chemins
    ctx.obj['no_addon'] = no_addon
    if user:
        if user not in config_user_obj.sections:
            click.secho('The user %s not found' % user, fg='red')
            sys.exit(-1)
        else:
            for k in user_keys:
                ctx.obj['user_%s' % k] = config_user_obj.get(user, k, '')
    if addon:
        if addon not in config_addon_obj.sections:
            click.secho('The addon %s not found' % addon, fg='red')
            sys.exit(-1)
        else:
            for k in addon_keys:
                ctx.obj['addon_%s' % k] = config_addon_obj.get(addon, k, '')
    if project:
        if project not in config_project_obj.sections:
            click.secho('The project %s not found' % project, fg='red')
            sys.exit(-1)
        else:
            for k in project_keys:
                ctx.obj['project_%s' % k] = config_project_obj.get(project, k, '')
    if not user:
        for _sec in config_user_obj.sections:
            default = 'default' in config_user_obj[_sec].keys() and config_user_obj.get(_sec).as_bool(
                'default') or False
            if default:
                user = _sec
    if not addon:
        for _sec in config_addon_obj.sections:
            default = 'default' in config_addon_obj[_sec].keys() and config_addon_obj.get(_sec).as_bool(
                'default') or False
            if default:
                addon = _sec
    if not project:
        for _sec in config_project_obj.sections:
            default = 'default' in config_project_obj[_sec].keys() and config_project_obj.get(_sec).as_bool(
                'default') or False
            if default:
                project = _sec
    ctx.obj['user'] = user
    ctx.obj['addon'] = addon
    ctx.obj['project'] = project
    ctx.obj['user_keys'] = user_keys
    ctx.obj['addon_keys'] = addon_keys
    ctx.obj['project_keys'] = project_keys
    ctx.obj['asset_keys'] = asset_keys
    ctx.obj['repo_keys'] = repo_keys
    ctx.obj['chemin_keys'] = chemin_keys
    ctx.obj['asset'] = False  # FIXME _
    ctx.obj['odoo_version'] = version
    if user:
        click.secho('Use the user %s as default' % user, fg='green')
    if addon:
        click.secho('Use the addon %s as default' % addon, fg='green')
    if project:
        click.secho('Use the project %s as default' % project, fg='green')
    ctx.obj['items'] = ['user', 'addon', 'project', 'asset']

    def check(*elements):
        return all([ctx.obj.get(__i, False) for __i in elements])

    ctx.obj['check'] = check


def make_this_default(__config, __section):
    for tmp_section in __config.sections:
        if tmp_section == __section:
            __config[tmp_section]['default'] = True
        else:
            __config[tmp_section]['default'] = False


def __get_items(key):
    if key == 'user':
        return 'user', USERS_FILE
    elif key == 'addon':
        return 'addon', ADDONS_FILE
    elif key == 'project':
        return 'project', PROJECTS_FILE
    elif key == 'asset':
        return 'asset', ASSETS_FILE
    elif key == 'repo':
        return 'repo', REPOS_FILE
    elif key == 'chemin':
        return 'chemin', CHEMINS_FILE


def __create_item(ctx, item_name, item_value):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('Create new %s %s to the config %s' % (key, item_value, config_path))
    if item_value not in config.sections:
        config[item_value] = {}
    else:
        click.secho('The %s %s already exists' % (key, item_value), fg='red')
        return
    for k in keys:
        default = ctx.obj.get('%s_%s' % (key, k), '')
        tmp = click.prompt(k, default=default, type=str)
        config[item_value][k] = tmp
    make_this_default(config, item_value)
    config.write()
    click.secho('The %s %s is created' % (key, item_value), fg='green')


def __update_item(ctx, item_name, item_value):
    key, config_path = __get_items(item_name)
    section = ctx.obj.get('%s' % item_name, False)
    item_value = item_value or section
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('Update %s %s from the config %s' % (key, item_value, config_path))
    if item_value not in config.sections:
        click.secho('The %s %s not found.' % (key, item_value), fg='red')
        return
    for k in keys:
        default = config[item_value].get(k, '')
        tmp = click.prompt(k, default=default, type=str)
        config[item_value][k] = tmp
    make_this_default(config, item_value)
    config.write()
    click.secho('The %s %s is updated' % (key, item_value), fg='green')


def __use_section(ctx, item_name, item_value):
    if not item_value:
        item_value = find_or_create_section_for(ctx, item_name)
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    click.echo('Update %s %s from the config %s' % (key, item_value, config_path))
    if item_value not in config.sections:
        click.secho('The %s %s not found.' % (key, item_value), fg='red')
        return
    make_this_default(config, item_value)
    config.write()
    click.secho('The %s %s will be used as default' % (key, item_value), fg='green')


def __delete_section(ctx, item_name, item_values):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    click.echo('Delete %s %s from the config %s' % (key, item_values, config_path))
    for item_value in item_values:
        if item_value not in config.sections:
            click.secho('The %s %s not found.' % (key, item_value), fg='red')
        else:
            del config[item_value]
            click.secho('The %s %s is removed' % (key, item_value), fg='green')
    with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
        config.write(configfile)


def __list_section(ctx, item_name):
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    click.echo('List %ss from the config %s' % (key, config_path))
    x = PrettyTable()
    x.field_names = [item_name.title()] + [k.title() for k in keys] + ['Default']
    for f in x.field_names:
        x.align[f] = 'l'
    for section in config.sections:
        data = [config[section].get(k, '') for k in keys]
        x.add_row([section] + data + [config[section].get('default', '')])
    click.echo(x)


def __get_all_keys(ctx, additional_keys={}):
    all_keys = {}
    for item in ctx.obj['items']:
        section = ctx.obj[item]
        if section:
            key, config_path = __get_items(item)
            config = ctx.obj['config_%s_obj' % key]
            keys = ctx.obj['%s_keys' % key]
            if section not in config.sections:
                click.secho('The %s %s not found.' % (item, section), fg='red')
                continue
            for k in keys:
                all_keys['%s_%s' % (item, k)] = config[section].get(k, '')
    all_keys.update(additional_keys)
    all_keys['odoo_version'] = ctx.obj['odoo_version']
    all_keys['assets'] = ctx.obj['assets']
    all_keys['repos'] = ctx.obj['repos']
    all_keys['chemins'] = ctx.obj['chemins']
    all_keys['addon_name_len'] = len(all_keys.get('addon_name', ''))
    all_keys['project_name_len'] = len(all_keys.get('project_name', ''))
    all_keys['addon_depends'] = [x.strip().lower() for x in
                                 all_keys.get('addon_depends', '').replace(',', ':').replace(';', ':').replace(' ',
                                                                                                               ':').split(
                                     ':') if x]
    return all_keys


def __fix_keys(ctx):
    for item in ctx.obj['items']:
        key, config_path = __get_items(item)
        config = ctx.obj['config_%s_obj' % key]
        keys = ctx.obj['%s_keys' % key]
        for section in config.sections:
            for _k in keys:
                if _k not in config[section].keys():
                    config.set(section, _k, '')
        with codecs.open(config_path, mode='wb', encoding='utf-8') as configfile:
            config.write(configfile)


def find_or_create_section_for(ctx, item_name):
    current_path = os.getcwd()
    key, config_path = __get_items(item_name)
    config = ctx.obj['config_%s_obj' % key]
    keys = ctx.obj['%s_keys' % key]
    for section in config.sections:
        if current_path == config[section].get('path', ''):
            make_this_default(config, section)
            return section
    section = click.prompt('Give a name for the item')
    config[section] = {}
    for k in keys:
        config[section][k] = ''
    config[section]['path'] = current_path
    make_this_default(config, section)
    config.write()
    return section


@cli.command()
@click.argument('user', type=click.STRING, required=True)
@click.pass_context
def user_create(ctx, user):
    """Create a new user"""
    __create_item(ctx, 'user', user)


@cli.command()
@click.argument('addon', type=click.STRING, required=True)
@click.pass_context
def addon_create(ctx, addon):
    """Create a new addon"""
    __create_item(ctx, 'addon', addon)


@cli.command()
@click.argument('project', type=click.STRING, required=True)
@click.pass_context
def project_create(ctx, project):
    """Create a new project"""
    __create_item(ctx, 'project', project)


@cli.command()
@click.argument('asset', type=click.STRING, required=True)
@click.pass_context
def asset_create(ctx, asset):
    """Create a new asset"""
    __create_item(ctx, 'asset', asset)


@cli.command()
@click.argument('chemin', type=click.STRING, required=True)
@click.pass_context
def path_create(ctx, chemin):
    """Create a new chemin"""
    __create_item(ctx, 'chemin', chemin)


@cli.command()
@click.argument('repo', type=click.STRING, required=True)
@click.pass_context
def repo_create(ctx, repo):
    """Create a new repo"""
    __create_item(ctx, 'repo', repo)


@cli.command()
@click.argument('user', type=click.STRING, required=False)
@click.pass_context
def user_update(ctx, user):
    """Update a user"""
    __update_item(ctx, 'user', user)


@cli.command()
@click.argument('addon', type=click.STRING, required=False)
@click.pass_context
def addon_update(ctx, addon):
    """Update an addon"""
    __update_item(ctx, 'addon', addon)


@cli.command()
@click.argument('project', type=click.STRING, required=False)
@click.pass_context
def project_update(ctx, project):
    """Update a project"""
    __update_item(ctx, 'project', project)


@cli.command()
@click.argument('asset', type=click.STRING, required=False)
@click.pass_context
def asset_update(ctx, asset):
    """Update an asset"""
    __update_item(ctx, 'asset', asset)


@cli.command()
@click.argument('repo', type=click.STRING, required=False)
@click.pass_context
def repo_update(ctx, repo):
    """Update a repo"""
    __update_item(ctx, 'repo', repo)


@cli.command()
@click.argument('chemin', type=click.STRING, required=False)
@click.pass_context
def path_update(ctx, chemin):
    """Update a path"""
    __update_item(ctx, 'chemin', chemin)


@cli.command()
@click.argument('user', type=click.STRING, required=True)
@click.pass_context
def user_use(ctx, user):
    """Use a user a default"""
    __use_section(ctx, 'user', user)


@cli.command()
@click.argument('project', type=click.STRING, required=False)
@click.pass_context
def project_use(ctx, project):
    """Use a project as default"""
    __use_section(ctx, 'project', project)


@cli.command()
@click.argument('asset', type=click.STRING, required=False)
@click.pass_context
def asset_use(ctx, asset):
    """Use an asset as default"""
    __use_section(ctx, 'asset', asset)


@cli.command()
@click.argument('addon', type=click.STRING, required=True)
@click.pass_context
def addon_use(ctx, addon):
    """Use an addon as default"""
    __use_section(ctx, 'addon', addon)


@cli.command()
@click.argument('repo', type=click.STRING, required=True)
@click.pass_context
def repo_use(ctx, repo):
    """Use a repo as default"""
    __use_section(ctx, 'repo', repo)


@cli.command()
@click.argument('chemin', type=click.STRING, required=False)
@click.pass_context
def path_use(ctx, chemin):
    """Use a path as default"""
    __use_section(ctx, 'chemin', chemin)


@cli.command()
@click.argument('user', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def user_delete(ctx, user):
    """Delete a user"""
    __delete_section(ctx, 'user', user)


@cli.command()
@click.argument('addon', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def addon_delete(ctx, addon):
    """Delete an addon"""
    __delete_section(ctx, 'addon', addon)


@cli.command()
@click.argument('project', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def project_delete(ctx, project):
    """Delete an project"""
    __delete_section(ctx, 'project', project)


@cli.command()
@click.argument('asset', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def asset_delete(ctx, asset):
    """Delete an asset"""
    __delete_section(ctx, 'asset', asset)


@cli.command()
@click.argument('chemin', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def path_delete(ctx, chemin):
    """Delete a path"""
    __delete_section(ctx, 'chemin', chemin)


@cli.command()
@click.argument('repo', type=click.STRING, required=True, nargs=-1)
@click.pass_context
def repo_delete(ctx, repo):
    """Delete a repo"""
    __delete_section(ctx, 'repo', repo)


@cli.command()
@click.pass_context
def users(ctx):
    """Show users"""
    __list_section(ctx, 'user')


@cli.command()
@click.pass_context
def addons(ctx):
    """Show addons"""
    __list_section(ctx, 'addon')


@cli.command()
@click.pass_context
def projects(ctx):
    """Show projects"""
    __list_section(ctx, 'project')


@cli.command()
@click.pass_context
def assets(ctx):
    """Show assets"""
    __list_section(ctx, 'asset')


@cli.command()
@click.pass_context
def repos(ctx):
    """Show repos"""
    __list_section(ctx, 'repo')


@cli.command()
@click.pass_context
def paths(ctx):
    """Show paths"""
    __list_section(ctx, 'chemin')


@cli.command()
@click.pass_context
def table(ctx):
    """Show the table"""
    __list_section(ctx, 'project')
    __list_section(ctx, 'user')
    __list_section(ctx, 'addon')
    __list_section(ctx, 'asset')
    __list_section(ctx, 'repo')
    __list_section(ctx, 'chemin')


@cli.command()
@click.pass_context
def keys(ctx):
    """Show the keys"""
    all_keys = __get_all_keys(ctx)
    x = PrettyTable()
    x.field_names = ['Key', 'Value']
    for f in x.field_names:
        x.align[f] = 'l'
    keys = sorted(all_keys.keys())
    for k in filter(lambda s: s not in ['asset', 'repo', 'path'], keys):
        x.add_row([k, all_keys.get(k)])
    click.echo(x)


@cli.command()
@click.pass_context
def fix_keys(ctx):
    """Fix the keys"""
    __fix_keys(ctx)
    click.secho('Keys are fixed', fg='green')


# ***************   GENERATING DATA   ***************#

def hash_model(m, prefix='', suffix='', ext=''):
    m = m.strip().lower()
    tmp = ''
    for x in m:
        tmp += x if x.isalnum() or x == '_' else '.'
    model_dot = tmp
    model_underscore = model_dot.replace('.', '_')
    model_class = tmp.replace('.', '_').title().replace('_', '')
    model_filename_tab = []
    for part in model_dot.split('.')[::-1]:
        if part not in model_filename_tab:
            model_filename_tab.append(part)
    model_filename = '_'.join(model_filename_tab[::-1]) if model_filename_tab else model_underscore
    if model_filename.startswith('ir_') and len(model_filename) > 3:
        model_filename = model_filename[3:]
    if model_filename.startswith('hr_') and len(model_filename) > 3:
        model_filename = model_filename[3:]
    if model_filename.startswith('res_') and len(model_filename) > 3:
        model_filename = model_filename[4:]
    if ext:
        ext = not ext.startswith('.') and ('.' + ext) or ext
    return model_dot, model_underscore, model_class, prefix + model_filename + suffix, prefix + model_filename + suffix + ext


def check_url_and_is_dir(url):
    if not url:
        return False, 'Please provide an URL %s' % url
    if not os.path.exists(url):
        return False, 'Url %s not found' % url
    if not os.path.isdir(url):
        return False, 'Url %s is not a directory' % url
    return True, os.path.abspath(url)


def check_url_and_is_file(url):
    if not url:
        return False, 'Please provide an URL' % url
    if not os.path.isfile(url):
        return False, 'Url %s is not a file' % url
    return True, os.path.abspath(url)


def check_url_and_is_addon(url):
    if not url:
        return False, 'Please provide an URL' % url
    if not os.path.isdir(url):
        return False, 'Url %s is not a directory' % url
    path_manifest = os.path.sep.join([url, MANIFEST_FILE])
    path_openerp = os.path.sep.join([url, OPENERP_FILE])
    if os.path.isfile(path_manifest):
        return True, path_manifest
    if os.path.isfile(path_openerp):
        return True, path_openerp
    return False, 'The directory %s is not an addon' % url


def fix_addon_version(_ap, all_keys):
    _ap_openerp_full = os.path.join(_ap, '__openerp__.py')
    _ap_odoo_full = os.path.join(_ap, '__manifest__.py')
    odoo_version = all_keys.get('odoo_version', False)
    if os.path.isfile(_ap_openerp_full) and (not odoo_version or odoo_version > 8 or odoo_version == 0):
        ___set_openerp()
        all_keys['odoo_version'] = 8
    if os.path.isfile(_ap_odoo_full) and (not odoo_version or odoo_version < 9):
        ___set_odoo()
        all_keys['odoo_version'] = 10
    return all_keys


def go_and_patch_addon(project_path, addon_slug, all_keys, depends=None, **kwargs):
    def _get_templates_attrs(_type, frontend=False, backend=False):
        _type = _type.lower().strip()
        _tag, _attr, _id, _inherit = 'link', {'rel': 'stylesheet', 'href': None}, 'assets_backend', 'web.assets_backend'
        if frontend:
            _id = 'assets_frontend'
            _inherit = 'website.assets_frontend'
        js = _type.startswith('js') and True or False
        if js:
            _tag, _attr = 'script', {'type': 'text/javascript', 'src': None}
        return _tag, _attr, _id, _inherit

    def fix_template_asset(_addon_path, _path, _type, frontend=False, backend=False):
        _tag, _attr, _id, _inherit = _get_templates_attrs(_type, frontend, backend)
        create_dir([_addon_path, VIEWS])
        templates_path = os.path.join(_addon_path, VIEWS, 'templates.xml')
        asset_file = '/' + _path
        create_file([_addon_path, VIEWS, 'templates.xml'], add_content='<?xml version="1.0" encoding="UTF-8"?>',
                    condition='<?xml', test_on_plat=True)
        create_file([_addon_path, VIEWS, 'templates.xml'], add_content='<%s>' % ODOO, test_on_plat=True)
        # create_file([_addon_path, VIEWS, 'templates.xml'], add_content='    <data>')
        # create_file([_addon_path, VIEWS, 'templates.xml'], add_content='    </data>')
        create_file([_addon_path, VIEWS, 'templates.xml'], add_content='</%s>' % ODOO, test_on_plat=True)
        add_to_manifest([addon_path, MANIFEST_FILE], [VIEWS, 'templates.xml'])
        template_node = etree.parse(templates_path)
        root = template_node.getroot()
        data = root.find('data')
        if data == None:
            data = root
        template_node = data.find("template[@id='%s']" % _id)
        _attr_key = 'unknown'
        for _k, _v in _attr.iteritems():
            if not _v:
                _attr_key = _k
                _attr[_k] = asset_file
        if template_node == None:
            template_node = etree.SubElement(data, 'template', id=_id, inherit_id=_inherit,
                                             name=all_keys.get('addon_slug', 'Name'))
        xpath = template_node.find('xpath')
        if xpath == None:
            xpath = etree.SubElement(template_node, 'xpath', expr='.', position='inside')
        file_node = xpath.find('%s[@%s="%s"]' % (_tag, _attr_key, asset_file))
        if file_node == None:
            etree.SubElement(xpath, _tag, **_attr)
        contents = etree.tostring(root, encoding='utf8', xml_declaration=True, pretty_print=True)
        create_file([_addon_path, VIEWS, 'templates.xml'], contents=contents)

    assets = all_keys.get('assets', {})
    click.echo('Patch the addon %s ...' % addon_slug)
    click.echo('args : %s' % kwargs)
    addon_path = os.path.join(project_path, addon_slug)
    if depends:
        depends = __clean_depends(depends)
        all_keys['addon_depends'] = depends
    if not os.path.exists(addon_path):
        os.mkdir(addon_path)
    fix_addon_version(addon_path, all_keys)
    manifest_path = os.path.join(addon_path, MANIFEST_FILE)
    root_init_path = os.path.join(addon_path, INIT_FILE)
    readme_path = os.path.join(addon_path, ADDON_README_FILE)
    if not os.path.isfile(manifest_path):
        with codecs.open(manifest_path, encoding='utf-8', mode='w+') as manifest_file:
            manifest_file.write(render(MANIFEST_TEMPLATE_FILE, all_keys))
    if not os.path.isfile(root_init_path):
        with codecs.open(root_init_path, mode='w+', encoding='utf-8') as manifest_file:
            manifest_file.write('')

    if kwargs.get('readme', []):
        readme = kwargs.get('readme', [])
        if readme:
            if not os.path.isfile(readme_path):
                with codecs.open(readme_path, mode='w+', encoding='utf-8') as addon_readme_file:
                    addon_readme_file.write(render(ADDON_README_TEMPLATE_FILE, all_keys))

    if kwargs.get('xml', []):
        xml = kwargs.get('xml', [])
        if xml:
            create_dir([addon_path, STATIC, SRC, XML])
            if hasattr(xml, '__iter__'):
                for model_class in xml:
                    model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(
                        model_class, prefix='', ext='xml')
                    xml_file = '/'.join([all_keys.get('addon_slug'), STATIC, SRC, XML, model_filename_ext])
                    create_file([xml_file], add_content='<?xml version="1.0" encoding="UTF-8"?>', condition='<?xml',
                                test_on_plat=True)
                    create_file([xml_file], add_content='<templates xml:space="preserve">', condition='templates',
                                test_on_plat=True)
                    create_file([xml_file], add_content='</templates>', condition='templates', test_on_plat=True)

                    add_to_manifest([addon_path, MANIFEST_FILE], [STATIC, SRC, XML, model_filename_ext], key='qweb')

    if kwargs.get('css_backend', []):
        css_backend = kwargs.get('css_backend', [])
        if css_backend:
            create_dir([addon_path, STATIC, SRC, CSS])
            if hasattr(css_backend, '__iter__'):
                for model_class in css_backend:
                    model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(
                        model_class, prefix='', ext='css')
                    css_file = '/'.join([all_keys.get('addon_slug'), STATIC, SRC, CSS, model_filename_ext])
                    create_file([css_file], add_content='')
                    fix_template_asset(addon_path, css_file, 'css', backend=True)

    if kwargs.get('css_frontend', []):
        css_frontend = kwargs.get('css_frontend', [])
        if css_frontend:
            create_dir([addon_path, STATIC, SRC, CSS])
            if hasattr(css_frontend, '__iter__'):
                for model_class in css_frontend:
                    model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(
                        model_class, prefix='', ext='css')
                    css_file = '/'.join([all_keys.get('addon_slug'), STATIC, SRC, CSS, model_filename_ext])
                    create_file([css_file], add_content='')
                    fix_template_asset(addon_path, css_file, 'css', frontend=True)

    if kwargs.get('js_backend', []):
        js_backend = kwargs.get('js_backend', [])
        if js_backend:
            create_dir([addon_path, STATIC, SRC, JS])
            if hasattr(js_backend, '__iter__'):
                for model_class in js_backend:
                    model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(
                        model_class, prefix='', ext='js')
                    js_file = '/'.join([all_keys.get('addon_slug'), STATIC, SRC, JS, model_filename_ext])
                    create_file([js_file], add_content='odoo.define(\'%s.%s\', function(require){' % (
                        all_keys.get('addon_slug', 'addon'), model_filename))
                    create_file([js_file], add_content='"use strict";')
                    create_file([js_file], add_content='});')
                    fix_template_asset(addon_path, js_file, 'js', backend=True)

    if kwargs.get('js_frontend', []):
        js_frontend = kwargs.get('js_frontend', [])
        if js_frontend:
            create_dir([addon_path, STATIC, SRC, JS])
            if hasattr(js_frontend, '__iter__'):
                for model_class in js_frontend:
                    model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(
                        model_class, prefix='', ext='js')
                    js_file = '/'.join([all_keys.get('addon_slug'), STATIC, SRC, JS, model_filename_ext])
                    create_file([js_file], add_content='')
                    fix_template_asset(addon_path, js_file, 'js', frontend=True)

    if kwargs.get('icon', []):
        icon = kwargs.get('icon', [])
        if icon:
            create_dir([addon_path, STATIC, DESCRIPTION])
            if hasattr(icon, '__iter__'):
                for ico in icon:
                    destination = os.path.join(addon_path, STATIC, DESCRIPTION, 'icon.png')
                    source = assets.get(ico, {}).get('path', False)
                    if source:
                        shutil.copyfile(source, destination)

    if kwargs.get('i18n', []):
        i18n = kwargs.get('i18n', [])
        if i18n:
            create_dir([addon_path, I18N])

    if kwargs.get('tests', []):
        tests = kwargs.get('tests', [])
        if tests:
            create_dir([addon_path, TESTS])
            create_file([addon_path, TESTS, INIT_FILE])
        if hasattr(tests, '__iter__'):
            for model_class in tests:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model_class,
                                                                                                          prefix='test_',
                                                                                                          ext='py')
                create_file([addon_path, TESTS, model_filename_ext], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, TESTS, model_filename_ext], add_content='from %s.tests import common' % ODOO)
                create_file([addon_path, TESTS, model_filename_ext],
                            add_content='class %s(common.TransactionCase):' % model_class)
                create_file([addon_path, TESTS, model_filename_ext], add_content='    def setUp(self):')
                create_file([addon_path, TESTS, model_filename_ext],
                            add_content='       super(%s, self).setUp()' % model_class)
                create_file([addon_path, TESTS, INIT_FILE], add_content='from . import %s' % model_filename)
    if kwargs.get('controllers', []):
        controllers = kwargs.get('controllers', [])
        if controllers:
            create_dir([addon_path, CONTROLLERS])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % CONTROLLERS)
            create_file([addon_path, CONTROLLERS, INIT_FILE], add_content='from . import main')
            create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE], add_content='# -*- coding: utf-8 -*-')
            create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE], add_content='import http, registry')
            create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                        add_content='from %s.http import request' % ODOO)
        if hasattr(controllers, '__iter__'):
            for model_class in controllers:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model_class,
                                                                                                          ext='py')
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='class %s(http.Controller):' % model_class)
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='    @http.route(\'/%s/index\', type=\'http\', auth="none")' % model_class)
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='    def %s_index(self, **kw):' % model_class)
                create_file([addon_path, CONTROLLERS, CONTROLLER_MAIN_FILE],
                            add_content='        pass  # %s' % model_class)
    if kwargs.get('models', []):
        models = kwargs.get('models')
        if models:
            create_dir([addon_path, MODELS])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % MODELS)
            create_file([addon_path, MODELS, INIT_FILE])
        if hasattr(models, '__iter__'):
            for model in models:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='py')
                create_file([addon_path, MODELS, model_filename_ext], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, MODELS, model_filename_ext],
                            add_content='from %s import models, fields, api, _' % ODOO)
                create_file([addon_path, MODELS, model_filename_ext],
                            add_content='class %s(models.Model):' % model_class)
                create_file([addon_path, MODELS, model_filename_ext], add_content='    _name = \'%s\'' % model_dot)
                create_file([addon_path, MODELS, INIT_FILE], add_content='from . import %s' % model_filename)
    if kwargs.get('inherit_models', []):
        inherit_models = kwargs.get('inherit_models')
        if inherit_models:
            create_dir([addon_path, MODELS])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % MODELS)
            create_file([addon_path, MODELS, INIT_FILE])
        if hasattr(inherit_models, '__iter__'):
            for model in inherit_models:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='py')
                create_file([addon_path, MODELS, model_filename_ext], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, MODELS, model_filename_ext],
                            add_content='from %s import models, fields, api, _' % ODOO)
                create_file([addon_path, MODELS, model_filename_ext],
                            add_content='class %s(models.Model):' % model_class)
                create_file([addon_path, MODELS, model_filename_ext], add_content='    _inherit = \'%s\'' % model_dot)
                create_file([addon_path, MODELS, INIT_FILE], add_content='from . import %s' % model_filename)
    if kwargs.get('views', []):
        views = kwargs.get('views', [])
        if views:
            create_dir([addon_path, VIEWS])
        if hasattr(views, '__iter__'):
            for model in views:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='xml')
                create_file([addon_path, VIEWS, model_filename_ext],
                            add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='<%s>' % ODOO)
                create_file([addon_path, VIEWS, model_filename_ext], add_content='    <data>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='    </data>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='</%s>' % ODOO)
                add_to_manifest([addon_path, MANIFEST_FILE], [VIEWS, model_filename_ext])

    if kwargs.get('inherit_views', []):
        inherit_views = kwargs.get('inherit_views', [])
        if inherit_views:
            create_dir([addon_path, VIEWS])
        if hasattr(inherit_views, '__iter__'):
            for model in inherit_views:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='xml')
                create_file([addon_path, VIEWS, model_filename_ext],
                            add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='<%s>' % ODOO)
                create_file([addon_path, VIEWS, model_filename_ext], add_content='    <data>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='    </data>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='</%s>' % ODOO)
                add_to_manifest([addon_path, MANIFEST_FILE], [VIEWS, model_filename_ext])

    if kwargs.get('wizard', []):
        wizard = kwargs.get('wizard', [])
        if wizard:
            create_dir([addon_path, WIZARD])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % WIZARD)
            create_file([addon_path, WIZARD, INIT_FILE])
        if hasattr(wizard, '__iter__'):
            for model in wizard:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='xml')
                create_file([addon_path, WIZARD, model_filename_ext],
                            add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='<%s>' % ODOO)
                create_file([addon_path, WIZARD, model_filename_ext], add_content='    <data>')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='    </data>')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='</%s>' % ODOO)
                add_to_manifest([addon_path, MANIFEST_FILE], [WIZARD, model_filename_ext])
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='py')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, WIZARD, model_filename_ext],
                            add_content='from %s import models, fields, api, _' % ODOO)
                create_file([addon_path, WIZARD, model_filename_ext],
                            add_content='class %s(models.TransientModel):' % model_class)
                create_file([addon_path, WIZARD, model_filename_ext], add_content='    _name = \'%s\'' % model_dot)
                create_file([addon_path, WIZARD, INIT_FILE], add_content='from . import %s' % model_filename)

    if kwargs.get('report', []):
        report = kwargs.get('report', [])
        if report:
            create_dir([addon_path, VIEWS])
        if hasattr(report, '__iter__'):
            for model in report:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='xml',
                                                                                                          suffix='_report')
                create_file([addon_path, VIEWS, model_filename_ext],
                            add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='<%s>' % ODOO)
                create_file([addon_path, VIEWS, model_filename_ext], add_content='    <data>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='    </data>')
                create_file([addon_path, VIEWS, model_filename_ext], add_content='</%s>' % ODOO)
                add_to_manifest([addon_path, MANIFEST_FILE], [VIEWS, model_filename_ext])

    if kwargs.get('parser', []):
        parser = kwargs.get('parser', [])
        if parser:
            create_dir([addon_path, REPORT])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % REPORT)
            create_file([addon_path, REPORT, INIT_FILE])
        if hasattr(parser, '__iter__'):
            for model in parser:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='py')
                create_file([addon_path, REPORT, model_filename_ext], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='from %s import models, fields, api, _' % ODOO)
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='class %s(models.AbstractModel):' % model_class)
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='    _name = \'report.%s\'' % model_dot)
                create_file([addon_path, REPORT, model_filename_ext], add_content='    @api.model')
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='    def render_html(self, docids, data=None):', )
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='        self.model = self.env.context.get(\'active_model\')', )
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='        docs = self.env[self.model].browse(self.env.context.get(\'active_ids\', []))', )
                create_file([addon_path, REPORT, model_filename_ext], add_content='        docargs = {', )
                create_file([addon_path, REPORT, model_filename_ext], add_content='            \'doc_ids\': docids,', )
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='            \'doc_model\': self.model,', )
                create_file([addon_path, REPORT, model_filename_ext], add_content='            \'docs\': docs,', )
                create_file([addon_path, REPORT, model_filename_ext], add_content='        }', )
                create_file([addon_path, REPORT, model_filename_ext],
                            add_content='        return self.env[\'report\'].render(\'%s\', docargs)' % model_dot, )
                create_file([addon_path, REPORT, INIT_FILE], add_content='from . import %s' % model_filename)

    if kwargs.get('inherit_wizard', []):
        inherit_wizard = kwargs.get('inherit_wizard', [])
        if inherit_wizard:
            create_dir([addon_path, WIZARD])
            create_file([addon_path, INIT_FILE], add_content='from . import %s' % WIZARD)
            create_file([addon_path, WIZARD, INIT_FILE])
        if hasattr(inherit_wizard, '__iter__'):
            for model in inherit_wizard:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='xml')
                create_file([addon_path, WIZARD, model_filename_ext],
                            add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='<%s>' % ODOO)
                create_file([addon_path, WIZARD, model_filename_ext], add_content='    <data>')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='    </data>')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='</%s>' % ODOO)
                add_to_manifest([addon_path, MANIFEST_FILE], [WIZARD, model_filename_ext])
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='py')
                create_file([addon_path, WIZARD, model_filename_ext], add_content='# -*- coding: utf-8 -*-')
                create_file([addon_path, WIZARD, model_filename_ext],
                            add_content='from %s import models, fields, api, _' % ODOO)
                create_file([addon_path, WIZARD, model_filename_ext],
                            add_content='class %s(models.TransientModel):' % model_class)
                create_file([addon_path, WIZARD, model_filename_ext], add_content='    _inherit = \'%s\'' % model_dot)
                create_file([addon_path, WIZARD, INIT_FILE], add_content='from . import %s' % model_filename)

    if kwargs.get('data', []):
        data = kwargs.get('data', [])
        if data:
            create_dir([addon_path, DATA])
        if hasattr(data, '__iter__'):
            for model in data:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model,
                                                                                                          ext='xml')
                create_file([addon_path, DATA, model_filename_ext],
                            add_content='<?xml version="1.0" encoding="UTF-8"?>')
                create_file([addon_path, DATA, model_filename_ext], add_content='<%s>' % ODOO)
                create_file([addon_path, DATA, model_filename_ext], add_content='    <data>')
                create_file([addon_path, DATA, model_filename_ext], add_content='    </data>')
                create_file([addon_path, DATA, model_filename_ext], add_content='</%s>' % ODOO)
                add_to_manifest([addon_path, MANIFEST_FILE], [DATA, model_filename_ext])
    if kwargs.get('security', []):
        security = kwargs.get('security', [])
        if security:
            create_dir([addon_path, SECURITY])
            create_file([addon_path, SECURITY, SECURITY_FILE],
                        add_content='id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink')
            add_to_manifest([addon_path, MANIFEST_FILE], [SECURITY, SECURITY_FILE])
        if hasattr(security, '__iter__'):
            for model in security:
                model_dot, model_underscore, model_class, model_filename, model_filename_ext = hash_model(model)
                create_file([addon_path, SECURITY, SECURITY_FILE],
                            add_content='access_%s_user,%s.user,model_%s,,1,0,0,0' % (
                                model_underscore, model_dot, model_underscore))
                create_file([addon_path, SECURITY, SECURITY_FILE],
                            add_content='access_%s_manager,%s.manager,model_%s,,1,1,1,1' % (
                                model_underscore, model_dot, model_underscore))

    click.secho("Addon <%s> patched in the project <%s>" % (addon_slug, project_path), fg='green')


def __clean_depends(deps):
    if hasattr(deps, '__iter__'):
        return list(deps)
    if isinstance(deps, basestring):
        deps = deps.strip().replace(' ', ':').replace(';', ';').replace(',', ':')
        deps = [x.strip().lower() for x in deps.split(':') if x.strip()]
    return deps


def create_dir(paths):
    path = os.path.sep.join(paths)
    if not os.path.exists(path):
        os.makedirs(path)


def add_to_manifest(manifest_paths, file_paths, key='data'):
    manifest_file = os.path.sep.join(manifest_paths)
    file_path = '/'.join(file_paths)
    _insert_manifest_item(manifest_file, key, file_path)


def _insert_manifest_item(manifest_file, key, item):
    """ Insert an item in the list of an existing manifest key """
    with codecs.open(manifest_file, ) as f:
        manifest = f.read()
    if item in eval(manifest).get(key, []):
        return
    pattern = """(["']{}["']:\\s*\\[)""".format(key)
    repl = """\\1\n        '{}',""".format(item)
    manifest = re.sub(pattern, repl, manifest, re.MULTILINE)
    with codecs.open(manifest_file, mode='w+', encoding='utf-8') as f:
        f.write(manifest.decode(encoding='utf-8'))


def create_file(paths, contents=None, add_content=None, condition=None, test_on_plat=False):
    assert hasattr(paths, '__iter__'), 'paths should be a list or tuple'
    py_file = os.path.sep.join(paths)
    if not os.path.isfile(py_file):
        with codecs.open(py_file, mode='w+', encoding='utf-8') as pyfile:
            pyfile.write('')
    if contents:
        if contents not in open(py_file, 'r').read():
            with codecs.open(py_file, mode='w+', encoding='utf-8') as pyfile:
                pyfile.write(contents)
    content_lines = [x.rstrip() for x in open(py_file, 'r').readlines() if x]
    plat_content = ''.join(content_lines).lower().strip()
    content_to_test = plat_content if test_on_plat else content_lines
    if add_content:
        if (not condition and add_content not in content_to_test) or (condition and condition not in content_to_test):
            with codecs.open(py_file, mode='a+', encoding='utf-8') as pyfile:
                if len(content_lines) > 0 and content_lines[-1].strip():
                    add_content = '\n' + add_content
                pyfile.write(add_content)


@cli.command()
@click.argument('module_name', type=click.STRING, required=False)
@click.pass_context
def addon_patch(ctx, module_name):
    """Create or update an addon"""
    all_keys = __get_all_keys(ctx, )
    if not ctx.obj['check']('user', 'project'):
        click.secho('please provide a user and a project', fg='red')
        return
    if not module_name and not ctx.obj['check']('addon'):
        click.secho('please provide an addon', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    if module_name and module_name != all_keys.get('addon_slug', False):
        all_keys['addon_slug'] = module_name
        project_addon_path = os.path.sep.join([all_keys.get('project_path', ''), module_name])
        pass_a, msg_a = check_url_and_is_addon(project_addon_path)
        if not pass_a:
            click.secho('Addon : %s' % msg_a, fg='red')
            return
    if not all_keys.get('addon_slug', False):
        click.secho('please provide a name of the addon', fg='red')
        return
    addon_slug = module_name or all_keys.get('addon_slug')
    project_path = all_keys.get('project_path')
    os.chdir(project_path)
    addon_path = os.path.join(project_path, addon_slug)
    all_keys = fix_addon_version(addon_path, all_keys)
    fuzzy_keywords = """
    Keywords:
    
    models inherit_models views inherit_views  wizard  inherit_wizard 
    data  controllers  security  i18n tests icon  description  readme 
    js_frontend css_frontend js_backend css_backend xml report parser
    """
    click.secho(fuzzy_keywords, fg='blue')
    if click.confirm('Continue to patch the addon <%s> in the project "%s" for the version <%s>' % (
            addon_slug, project_path, all_keys.get('odoo_version'))):
        fuzzy = click.prompt('Enter the fuzzy string')
        fuzzy = fuzzy.strip().lower()
        to_replace = ' ,:;-/@#&+'
        for tr in to_replace:
            fuzzy = fuzzy.replace(tr, '=')
        fuzzy = [x.strip() for x in fuzzy.split('=') if x]
        models = []
        groups = {}
        item_found = False
        for item in fuzzy:
            if item in ['js', 'css']:
                click.secho('Please indicate if it is backend or frontend, backend will be used as default',
                            fg='yellow')
                item += '_backend'
            if item.startswith('js') and item not in ['js_frontend', 'js_backend']:
                item2 = 'js_backend'
                click.secho('%s is not recognized, we will use %s' % (item, item2), fg='yellow')
                item = item2
            if item.startswith('css') and item not in ['css_frontend', 'css_backend']:
                item2 = 'css_backend'
                click.secho('%s is not recognized, we will use %s' % (item, item2), fg='yellow')
                item = item2
            if item.strip().lower().replace('_', '').replace('s', '') in ['inheritmodel', 'modelinherit']:
                item = 'inherit_models'
            if item.strip().lower().replace('_', '').replace('s', '') in ['inheritview', 'viewinherit']:
                item = 'inherit_views'
            if item.strip().lower().replace('_', '').replace('s', '') in ['inheritwizard', 'wizardinherit']:
                item = 'inherit_wizard'
            if item in ['models', 'inherit_models', 'views', 'inherit_views', 'wizard', 'inherit_wizard', 'data',
                        'controllers', 'security', 'i18n', 'tests', 'icon',
                        'description', 'readme', 'js_frontend', 'css_frontend', 'js_backend', 'css_backend', 'xml',
                        'report', 'parser']:
                if item not in groups:
                    groups[item] = models[:] or True
                else:
                    if hasattr(groups[item], '__iter__'):
                        groups[item] += models[:]
                item_found = True
            else:
                if item_found:
                    models = []
                    item_found = False
                models.append(item)
        go_and_patch_addon(all_keys.get('project_path'), all_keys.get('addon_slug'), all_keys, **groups)
    else:
        click.secho('Exit', fg='red')


@cli.command()
@click.pass_context
def project_patch(ctx):
    """Init or patch a project"""
    all_keys = __get_all_keys(ctx)
    if not ctx.obj['check']('user', 'project'):
        click.secho('please provide a user and a project', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    if not all_keys.get('project_slug', False):
        click.secho('please provide a slug for the project', fg='red')
        return
    project_slug = all_keys.get('project_slug', '')
    project_name = all_keys.get('project_name', '')
    addons = {
        '%s_base' % project_slug: {
            'addon_depends': 'base',
            'addon_slug': '%s_base' % project_slug,
            'addon_name': '%s - Base' % project_name,
            'addon_category': 'Tools',
            'addon_summary': 'Module de base pour %s' % project_name,
            'addon_description': u"""
L'objectif de ce module est :
* Déclarer toutes les dépendances avec les modules standard et communautaires d'Odoo
* Ce module doit être déclaré dans les nouveaux modules créés
* Pour les nouveaux modules, il ne devrait pas dépendre des modules standard mais de ce module
* Pour mettre à jour les modules du projet, il suffit de mettre à jour ce module""",
        },
        '%s_recette' % project_slug: {
            'addon_depends': '%s_base' % project_slug,
            'addon_slug': '%s_recette' % project_slug,
            'addon_name': '%s - Recette' % project_name,
            'addon_category': 'Tools',
            'addon_summary': 'Module de recette pour %s' % project_name,
            'addon_description': u"""
L'objectif de ce module est de :
* Dépendre de tous les les modules spécifiques du projet
* Installer tous les modules lorsque ce module est installé
* Paraméter les données de la société""",
            'args': {
                'data': ['company'],
            }
        },
        '%s_demo' % project_slug: {
            'addon_depends': '%s_recette' % project_slug,
            'addon_slug': '%s_demo' % project_slug,
            'addon_name': u'%s - Démo' % project_name,
            'addon_category': 'Tools',
            'addon_summary': u'Module de démonstration pour %s' % project_name,
            'addon_description': u"""
L'objectif de ce module est de :
* Préparer des données pour la démonstration""",
            'args': {
                'data': True,
            }
        },
    }
    for addon, additional_keys in addons.iteritems():
        all_keys = __get_all_keys(ctx, additional_keys)
        go_and_patch_addon(all_keys.get('project_path'), all_keys.get('addon_slug'), all_keys,
                           **additional_keys.get('args', {}))
    readme_path = os.path.join(all_keys.get('project_path'), PROJECT_README_FILE)
    if not os.path.isfile(readme_path):
        with codecs.open(readme_path, encoding='utf-8', mode='w+') as readme_file:
            readme_file.write(render(PROJECT_README_TEMPLATE_FILE, all_keys))


@cli.command()
@click.argument('addon', type=click.STRING, required=False)
@click.option('model', '-m', type=click.STRING, default=[], multiple=True, required=False)
@click.option('field', '-f', type=click.STRING, default=[], multiple=True, required=False)
@click.pass_context
def models(ctx, addon, model, field):
    """Show addon models"""
    all_keys = __get_all_keys(ctx)
    if not ctx.obj['check']('project'):
        click.secho('please provide a project', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    project_path = all_keys.get('project_path')
    if addon:
        project_path = os.path.join(project_path, addon)
    elif not ctx.obj['no_addon'] and all_keys.get('addon_slug', ''):
        project_path = os.path.join(project_path, all_keys.get('addon_slug'))
    click.secho('Dir to scan is %s' % project_path, fg='blue')
    project_dir = odooast.AstDir(project_path)
    astobj = odooast.AstFile(project_dir.get_py_files())
    ast_models = astobj.get_models(model_args=model, field_args=field)
    x = PrettyTable()
    x.field_names = ['Model', 'Base Class', 'Inherit']
    for f in x.field_names:
        x.align[f] = 'l'
    for ast_model, ast_model_data in ast_models:
        model_classes = ast_model_data.get('classes', [])
        model_base_classes = ast_model_data.get('base_classes', [])
        model_inherits = ast_model_data.get('inherits', [])
        x.add_row([ast_model, ', '.join(model_base_classes), ', '.join(model_inherits)])
    click.echo(x)


@cli.command()
@click.argument('addon', type=click.STRING, required=False)
@click.option('model', '-m', type=click.STRING, default=[], multiple=True, required=False)
@click.option('field', '-f', type=click.STRING, default=[], multiple=True, required=False)
@click.pass_context
def fields(ctx, addon, model, field):
    """Show addon fields for all models"""
    all_keys = __get_all_keys(ctx)
    if not ctx.obj['check']('project'):
        click.secho('please provide a project', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    project_path = all_keys.get('project_path')
    if addon:
        project_path = os.path.join(project_path, addon)
    elif not ctx.obj['no_addon'] and all_keys.get('addon_slug', ''):
        project_path = os.path.join(project_path, all_keys.get('addon_slug'))
    project_dir = odooast.AstDir(project_path)
    astobj = odooast.AstFile(project_dir.get_py_files())
    ast_models = astobj.get_models(model_args=model, field_args=field)
    click.secho('Dir to scan is %s, model=%s, found=%s' % (project_path, model, len(ast_models)), fg='blue')
    for ast_model, ast_model_data in ast_models:
        click.secho('', fg='blue')
        click.secho('Model : %s, Inherits : %s' % (ast_model, ','.join(ast_model_data.get('inherits', []))), fg='blue')
        for ast_model_path in ast_model_data.get('paths', []):
            click.secho('Path : %s' % ast_model_path, fg='blue')
        x = PrettyTable()
        x.field_names = ['Field', 'Type', 'Main', 'Required', 'OnChange', 'Compute', 'Inverse', 'Search', 'Store']
        for f in x.field_names:
            x.align[f] = 'l'
        for _field, field_data in ast_model_data.get('fields', {}).iteritems():
            field_type = field_data.get('type', '')
            field_required = field_data.get('required', '')
            field_onchange = field_data.get('onchange', '')
            field_compute = field_data.get('compute', '')
            field_inverse = field_data.get('inverse', '')
            field_search = field_data.get('search', '')
            field_store = field_data.get('store', '')
            field_relation = field_data.get('comodel_name', '')
            if field_type and '2' in str(field_type):
                if not field_relation:
                    field_relation = field_data.get('relation', '')
                if not field_relation:
                    field_relation = field_data.get('without_0', '')
            x.add_row([_field, l(field_type), l(field_relation), l(field_required), l(field_onchange), l(field_compute),
                       l(field_inverse),
                       l(field_search), l(field_store)])
        click.echo(x)


@cli.command()
@click.argument('addon', type=click.STRING, required=False)
@click.option('model', '-m', type=click.STRING, default=[], multiple=True, required=False)
@click.option('func', '-f', type=click.STRING, default=[], multiple=True, required=False)
@click.pass_context
def funcs(ctx, addon, model, func):
    """Show addon functions for all models"""
    all_keys = __get_all_keys(ctx)
    if not ctx.obj['check']('project'):
        click.secho('please provide a project', fg='red')
        return
    pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
    if not pass_p:
        click.secho('Project : %s' % msg_p, fg='red')
        return
    project_path = all_keys.get('project_path')
    if addon:
        project_path = os.path.join(project_path, addon)
    elif not ctx.obj['no_addon'] and all_keys.get('addon_slug', ''):
        project_path = os.path.join(project_path, all_keys.get('addon_slug'))
    project_dir = odooast.AstDir(project_path)
    astobj = odooast.AstFile(project_dir.get_py_files())
    ast_models = astobj.get_models(model_args=model, func_args=func)
    click.secho('Dir to scan is %s, model=%s, found=%s' % (project_path, model, len(ast_models)), fg='blue')
    for ast_model, ast_model_data in ast_models:
        click.secho('', fg='blue')
        click.secho('Model : %s, Inherits : %s' % (ast_model, ','.join(ast_model_data.get('inherits', []))), fg='blue')
        for ast_model_path in ast_model_data.get('paths', []):
            click.secho('Path : %s' % ast_model_path, fg='blue')
        x = PrettyTable()
        x.field_names = ['Func', 'Args']
        for f in x.field_names:
            x.align[f] = 'l'
        for _func, func_data in ast_model_data.get('funcs', {}).iteritems():
            x.add_row([_func, l(','.join([str(y) for y in func_data]), 80)])
        click.echo(x)


@cli.command()
@click.option('--here', '-h', is_flag=True, type=click.BOOL, default=False)
@click.option('--external', '-e', is_flag=True, type=click.BOOL, default=False)
@click.option('--addon', '-a', type=click.STRING, multiple=True)
@click.option('--recursion', '-r', is_flag=True, type=click.BOOL, default=False)
@click.pass_context
def tree(ctx, here, external, addon, recursion):
    """Show the addons tree"""
    filter_addon = addon
    all_keys = __get_all_keys(ctx)
    if not here:
        if not ctx.obj['check']('project'):
            click.secho('please provide a project', fg='red')
            return
        pass_p, msg_p = check_url_and_is_dir(all_keys.get('project_path', ''))
        if not pass_p:
            click.secho('Project : %s' % msg_p, fg='red')
            return
        project_path = all_keys.get('project_path')
    else:
        project_path = os.getcwd()
    addons = {}
    for root, dirs, files in os.walk(project_path):
        for name in files:
            file = os.path.join(root, name)
            if name in ['__openerp__.py', '__manifest__.py']:
                addon = os.path.basename(root)
                depends = eval(open(file).read()).get('depends', [])
                addons[addon] = depends
    arbre = ['root', []]
    root = arbre[1]
    node_result = None

    def get_node(root, item):
        global node_result
        node_result = None

        def _get_node(_arbre, item):
            global node_result
            if _arbre and isinstance(_arbre, list):
                if isinstance(_arbre[0], basestring):
                    if item == _arbre[0]:
                        if node_result is None:
                            node_result = []
                        if _arbre[1] not in node_result:
                            node_result.append(_arbre[1])
                    else:
                        _get_node(_arbre[1], item)
                else:
                    for obj in _arbre:
                        _get_node(obj, item)

        _get_node(root, item)
        return node_result if node_result is not None else [root]

    external_dependecies = filter(lambda r: r not in addons.keys(), list(set(Operator.flat(addons.values()))))
    if external:
        for ext_depend in external_dependecies:
            root.append([ext_depend, []])
    to_process, processed = addons.keys(), []

    def rotate(l):
        x = -1
        return l[-x:] + l[:-x]

    conflicts = {}
    hits = []
    while to_process:
        addon, depends = to_process[0], addons[to_process[0]]
        has_dependencies = False
        to_rotate, just_rotate = False, False
        for depend in depends:
            if not external and depend not in addons.keys():
                continue
            has_dependencies = True
            if depend in to_process:
                if addon not in hits:
                    hits.append(addon)
                    just_rotate = True
                    break
                conflicts[(addon, depend)] = conflicts.get((addon, depend), 0) + 1
                to_rotate = True
                break
            parents = get_node(root, depend)
            item_addon = [addon, []]
            for parent in parents:
                if item_addon not in parent:
                    parent.append(item_addon)
        if just_rotate:
            to_process = rotate(to_process)
            continue
        if to_rotate:
            to_process = rotate(to_process)
            for depend in depends:
                if conflicts.get((addon, depend), 1) > 1:
                    Log.warn("Recursion on addons %s <=> %s" % (addon, depend))
                    to_process.remove(addon)
                    processed.append(addon)
                    break
            continue
        if not has_dependencies:
            root.append([addon, []])
        to_process.remove(addon)
        processed.append(addon)
    if recursion:
        Log.success('End of verification.', exit=True)

    def filter_addons(arbre, whitelist):
        full_list = arbre
        to_delete = []

        def drop_subtree(full_list, whitelist, to_delete):
            values = full_list[1]
            for i, value in enumerate(values):
                if not (set(whitelist) & set(Operator.flat(value))):
                    to_delete.append((full_list, values, values[i], i))
                else:
                    for next_item in values:
                        drop_subtree(next_item, whitelist, to_delete)

        drop_subtree(full_list, whitelist, to_delete)
        while to_delete:
            full_list, values, value, index = to_delete[0]
            if value in full_list[1]:
                index = full_list[1].index(value)
                del full_list[1][index]
            del to_delete[0]
        return arbre

    if filter_addon:
        arbre = filter_addons(arbre, filter_addon)
    Log.info(format_tree(
        arbre, format_node=itemgetter(0), get_children=itemgetter(1)))


@cli.command()
@click.pass_context
def where(ctx):
    """Show project path"""
    all_keys = __get_all_keys(ctx)
    project_path = all_keys.get('project_path', '')
    addon_slug = all_keys.get('addon_slug', '')
    click.echo("Project path : %s" % project_path)
    click.echo("Addon slug : %s" % addon_slug)


#################### GIT RELATED COMMANDS

def __init_path_with_branches(tmp_path, tmp_branches):
    for tmp_br in tmp_branches:
        tmp_path_branch = os.path.join(tmp_path, tmp_br)
        try:
            os.makedirs(tmp_path_branch)
        except:
            pass


def __execute_git_command(cmd, git_url, git_dest, git_branch, git_depth, folder_name=None, git_n=4):
    git_dest = os.path.normpath(git_dest)
    os.chdir(git_dest)
    if cmd == 'clone':
        cmds = ['git', 'clone', git_url]
        if git_depth > 0:
            cmds += ['--depth', str(git_depth)]
        if git_branch:
            cmds += ['-b', git_branch]
        if folder_name:
            cmds += [folder_name]
    elif cmd == 'checkout':
        if folder_name:
            os.chdir(os.path.join(git_dest, folder_name))
        cmds = ['git', 'checkout', git_branch]
    elif cmd == 'pull':
        if folder_name:
            os.chdir(os.path.join(git_dest, folder_name))
        cmds = ['git', 'pull', 'origin', git_branch]
        if git_depth > 0:
            cmds += ['--depth', str(git_depth)]
    elif cmd == 'status':
        if folder_name:
            os.chdir(os.path.join(git_dest, folder_name))
        cmds = ['git', 'status']
    elif cmd == 'log':
        if folder_name:
            os.chdir(os.path.join(git_dest, folder_name))
        cmds = ['git', 'log', '--pretty=format:"%h%x09%x09%ad%x09%s', '--date', 'iso']
        if git_n > 0:
            cmds += ['-%s' % git_n]
    click.secho('Directory : %s' % os.getcwd(), fg='yellow')
    click.secho('URL : %s, Branch : %s' % (git_url, git_branch), fg='yellow')
    click.secho('Cmd : %s' % ' '.join(cmds), fg='yellow')
    click.echo("-" * 40)
    p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        click.secho(err, fg='red')
        click.echo("-" * 40)
        return False
    if out:
        click.secho(out, fg='green')
    click.echo("-" * 40)
    click.echo("\n\n")
    return True


def __get_git_vars(ctx, repos, path, branch, all, depth, number):
    if isinstance(repos, basestring):
        repos = repos.replace(',', ';').split(';')
    result = []
    all_keys = __get_all_keys(ctx)
    if not repos:
        click.secho('Please provide some repos', fg='red')
        return False
    for repo in repos:
        repo_arg = repo
        repo = all_keys.get('repos', {}).get(repo_arg, False)
        if not repo:
            click.secho('The repo %s is not found' % (repo or repo_arg), fg='red')
            return False
        if path:
            if os.path.isdir(path):
                pass
            else:
                path = all_keys.get('chemins', {}).get(path, {}).get('path', False)
                if not path:
                    click.secho('The path %s is not found' % path, fg='red')
                    return False
        else:
            path = all_keys.get('chemins', {}).get('PR', {}).get('path', False)
            if not path:
                click.secho('The path %s is not found' % path, fg='red')
                return
        branches = []
        for _k, _v in all_keys.get('repos').get(repo_arg).iteritems():
            if _k.startswith('branch_'):
                _k = _k[7:]
                if _v:
                    branches.append((_k, _v))
        if not all:
            if not branch:
                click.secho('Please specify a branch')
                return False
            branches = filter(lambda (m, n): m in branch or n in branch, branches)
        branch_paths = [x[0] for x in branches]
        branch_names = [x[1] for x in branches]
        if not os.path.isdir(path):
            click.secho('The path %s is not found' % path, fg='red')
            return False
        __init_path_with_branches(path, branch_paths)
        for br_path, br_name in branches:
            branch_path = os.path.join(path, br_path)
            result.append((repo.get('path'), branch_path, br_name, depth, repo_arg, number))
    return result


@cli.command()
@click.argument('cmds', type=click.STRING, required=True)
@click.argument('repos', type=click.STRING, required=True)
@click.argument('path', type=click.STRING, required=False)
@click.option('branch', '-b', type=click.STRING, default=[], multiple=True, required=False)
@click.option('--all', type=click.BOOL, default=False, is_flag=True)
@click.option('--depth', type=click.INT, default=1)
@click.option('-n', '--number', type=click.INT, default=4)
@click.pass_context
def git(ctx, cmds, repos, path, branch, all, depth, number):
    """pull2 a repository"""
    cmds = cmds.replace(',', ';').split(';') if isinstance(cmds, basestring) else cmds
    results = __get_git_vars(ctx, repos, path, branch, all, depth, number)
    if not results: return
    for git_path, git_dir, git_branch, git_depth, git_dirname, git_number in results:
        for cmd in cmds:
            if cmd == 'pull':
                __execute_git_command('checkout', git_path, git_dir, git_branch, git_depth, git_dirname, git_number)
                __execute_git_command('pull', git_path, git_dir, git_branch, git_depth, git_dirname, git_number)
            elif cmd == 'log':
                __execute_git_command('log', git_path, git_dir, git_branch, git_depth, git_dirname, git_number)
            elif cmd == 'status':
                __execute_git_command('status', git_path, git_dir, git_branch, git_depth, git_dirname, git_number)
            elif cmd == 'clone':
                __execute_git_command('clone', git_path, git_dir, git_branch, git_depth, git_dirname, git_number)
            else:
                click.secho('The command %s is not implemented' % cmd, fg='red')


if __name__ == '__main__':
    cli(obj={})


def main():
    return cli(obj={})
