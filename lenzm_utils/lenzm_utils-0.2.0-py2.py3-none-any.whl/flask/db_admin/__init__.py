"""Perform database admin tasks including migrations using Alembic.
"""
import logging

from flask import current_app
from flask.cli import AppGroup
import click

from . import migrate, pg

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

cli = AppGroup(name='db', help='Database Administration')
cli.add_command(migrate.cli)
cli.add_command(pg.cli)


@cli.command()
def create_all():
	"""Create database and objects."""
	logger.info('creating all')
	current_app.extensions['sqlalchemy'].db.create_all()


@cli.command()
@click.confirmation_option(help='Are you sure you want to drop the db?')
def drop_all():
	"""Drop all database objects (drop_all & create_all)."""
	logger.info('dropping all')
	current_app.extensions['sqlalchemy'].db.drop_all()


@cli.command()
def reset_all():
	"""Drop and recreate all objects."""
	if click.confirm('Are you sure you want to drop all data?'):
		logger.info('dropping all')
		current_app.extensions['sqlalchemy'].db.drop_all()
		logger.info('creating all')
		current_app.extensions['sqlalchemy'].db.create_all()
