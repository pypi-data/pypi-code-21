"""Perform database migrations using Alembic.

This is a click wrapper around the alembic library.
"""
import logging
import os

from flask import current_app
from flask.cli import AppGroup
import click
import alembic
import alembic.config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_DIR = 'migrations'
EXT_NAME = 'migrate'
HELP = {
	'autogenerate': (
		'Populate revision script with candidate migration '
		'operations, based on comparison of database to model.'
		),
	'branch-label': 'Specify a branch label to apply to the new revision',
	'head': 'Specify head revision or <branchname>@head to base new revision on.',
	'message': "Message string to use with 'revision'",
	'resolve-dependencies': 'Treat dependency versions as down revisions',
	'rev-id': 'Specify a hardcoded revision id instead of generating one',
	'rev-range': 'Specify a revision range; format is [start]:[end]',
	'splice': 'Allow a non-head revision as the "head" to splice onto',
	'sql': "Don't emit SQL to database - dump to standard output/file instead",
	'tag': "Arbitrary 'tag' name - can be used by custom env.py scripts.",
	'verbose': 'Use more verbose output',
	'version-path': 'Specify specific path from config for version file',
	'x-arg': "Additional arguments consumed by custom env.py scripts",
	}


class _MigrateConfig(object):
	def __init__(self, directory, db, **kwargs):
		self.directory = directory
		self.db = db
		self.configure_args = kwargs


class Migrate(object):
	"""Flask extension for alembic migrations."""
	def __init__(self, app=None, db=None, directory=DEFAULT_DIR, **kwargs):
		if app is not None:
			self.init_app(app, db, directory, **kwargs)

	def init_app(self, app, db=None, directory=DEFAULT_DIR, **kwargs):
		if not hasattr(app, 'extensions'):
			app.extensions = {}
		app.extensions[EXT_NAME] = _MigrateConfig(directory, db, **kwargs)


class Config(alembic.config.Config):
	def get_template_directory(self):
		package_dir = os.path.abspath(os.path.dirname(__file__))
		return os.path.join(package_dir, 'templates')


def _get_config(x_arg=None):
	directory = current_app.extensions[EXT_NAME].directory
	config = Config(os.path.join(directory, 'alembic.ini'))
	config.set_main_option('script_location', directory)
	if x_arg is not None:
		if config.cmd_opts is None:
			config.cmd_opts = lambda: None
		if not getattr(config.cmd_opts, 'x', None):
			config.cmd_opts.x = []
		config.cmd_opts.x.append(x_arg)
	return config


cli = AppGroup(help=__doc__, name='migrate')


@cli.command()
def init():
	"""Generates a new migration"""
	directory = current_app.extensions[EXT_NAME].directory
	config = Config()
	config.set_main_option('script_location', directory)
	config.config_file_name = os.path.join(directory, 'alembic.ini')
	alembic.command.init(config, directory, 'flask')


@cli.command()
@click.option('-m', '--message', help=HELP['message'])
@click.option(
	'--autogenerate/--no-autogenerate',
	default=True,
	help=HELP['autogenerate'],
	)
@click.option('--sql', is_flag=True, help=HELP['sql'])
@click.option('--head', default='head', help=HELP['head'])
@click.option('--splice', is_flag=True, help=HELP['splice'])
@click.option('--branch-label', help=HELP['branch-label'])
@click.option('--version-path', help=HELP['version-path'])
@click.option('--rev-id', help=HELP['rev-id'])
def revision(
	message,
	autogenerate,
	sql,
	head,
	splice,
	branch_label,
	version_path,
	rev_id,
	):
	"""Create a new revision file."""
	config = _get_config()
	alembic.command.revision(
		config,
		message,
		autogenerate=autogenerate,
		sql=sql,
		head=head,
		splice=splice,
		branch_label=branch_label,
		version_path=version_path,
		rev_id=rev_id,
		)


@cli.command()
@click.argument('revisions', nargs=-1)
@click.option('-m', '--message', help=HELP['message'])
@click.option('--branch-label', help=HELP['branch-label'])
@click.option('--rev-id', help=HELP['rev-id'])
def merge(revisions, message, branch_label, rev_id):
	"""Merge two revisions together.  Creates a new migration file.

	revisions is a list of one or more revisions, or 'heads' for all heads.
	"""
	config = _get_config()
	alembic.command.merge(
		config,
		revisions,
		message=message,
		branch_label=branch_label,
		rev_id=rev_id,
		)


@cli.command()
@click.argument('revision', required=False, default='head')
@click.option('--tag', help=HELP['tag'])
@click.option('--sql', is_flag=True, help=HELP['sql'])
@click.option('-x', '--x-arg', help=HELP['x-arg'])
def upgrade(revision, sql, tag, x_arg):
	"""Upgrade to a later version.

	revision is the identifier of the revision to upgrade to.
	"""
	config = _get_config(x_arg=x_arg)
	alembic.command.upgrade(config, revision, sql=sql, tag=tag)


@cli.command()
@click.argument('revision', required=False, default='-1')
@click.option('--tag', help=HELP['tag'])
@click.option('--sql', is_flag=True, help=HELP['sql'])
@click.option('-x', '--x-arg', help=HELP['x-arg'])
def downgrade(revision, sql, tag, x_arg):
	"""Revert to a previous version

	revision is the identifier of the revision to downgrade to.
	"""
	config = _get_config(x_arg=x_arg)
	if sql and revision == '-1':
		revision = 'head:-1'
	alembic.command.downgrade(config, revision, sql=sql, tag=tag)


@cli.command()
@click.argument('revision', required=False, default='head')
def show(revision):
	"""Show the revision denoted by the given symbol."""
	config = _get_config()
	alembic.command.show(config, revision)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help=HELP['verbose'])
@click.option('-r', '--rev-range', help=HELP['rev-range'])
def history(rev_range, verbose):
	"""List changeset scripts in chronological order."""
	config = _get_config()
	alembic.command.history(config, rev_range, verbose=verbose)


@cli.command()
@click.option(
	'--resolve-dependencies',
	is_flag=True,
	help=HELP['resolve-dependencies'],
	)
@click.option('-v', '--verbose', is_flag=True, help=HELP['verbose'])
def heads(verbose, resolve_dependencies):
	"""Show current available heads in the script directory"""
	config = _get_config()
	alembic.command.heads(
		config,
		verbose=verbose,
		resolve_dependencies=resolve_dependencies,
		)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help=HELP['verbose'])
def branches(verbose):
	"""Show current branch points"""
	config = _get_config()
	alembic.command.branches(config, verbose=verbose)


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help=HELP['verbose'])
def current(verbose, head_only):
	"""Display the current revision for each database."""
	config = _get_config()
	alembic.command.current(config, verbose=verbose)


@cli.command()
@click.option('--tag', help=HELP['tag'])
@click.option('--sql', is_flag=True, help=HELP['sql'])
@click.argument('revision', required=False, default='head')
def stamp(revision, sql, tag):
	"""'stamp' the revision table with the given revision; don't run any
	migrations"""
	config = _get_config()
	alembic.command.stamp(config, revision, sql=sql, tag=tag)
