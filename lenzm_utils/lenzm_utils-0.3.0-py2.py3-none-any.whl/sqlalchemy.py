import csv
import logging
import os.path

from flask import abort
import flask_sqlalchemy
from sqlalchemy import (
	types,
	Column,
	Integer,
	String,
	ForeignKey,
	)
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.collections import (
	InstrumentedList,
	InstrumentedSet,
	InstrumentedDict,
	)
import pytz

logger = logging.getLogger(__name__)
db = flask_sqlalchemy.SQLAlchemy()


def foreign_key_col(col, **kwargs):
	return Column(
		col.type,
		ForeignKey(col, ondelete='CASCADE', onupdate='CASCADE'),
		**kwargs
		)


def parent_key(column, col_type=Integer, nullable=False, index=True, **kwargs):
	return foreign_key_col(column, nullable=nullable, index=index, **kwargs)


class UTCDateTime(types.TypeDecorator):
	"""Type for storing and retrieving DateTimes as UTC.

	Naive datetimes are assumed to be UTC.
	The returned value is always a non-naive UTC datetime.
	"""

	impl = types.TIMESTAMP(timezone=True)

	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		if value.tzinfo is None:
			raise ValueError('Cannot handle naive datetime')
		return value.astimezone(pytz.utc)

	def process_result_value(self, value, dialect):
		if value is None:
			return None
		return value.astimezone(pytz.utc)


class BaseMixin():
	@classmethod
	def find_one(cls, **kwargs):
		return cls.query.filter_by(**kwargs).one()

	@classmethod
	def find_one_or_404(cls, **kwargs):
		try:
			cls.find_one(**kwargs)
		except (NoResultFound, MultipleResultsFound):
			abort(404)

	@classmethod
	def create(cls, **kwargs):
		obj = cls(**kwargs)
		cls.query.session.add(obj)
		return obj

	@classmethod
	def find_create(cls, create_args=None, **kwargs):
		try:
			return cls.find_one(**kwargs)
		except NoResultFound:
			create_args = dict(create_args or {})
			create_args.update(kwargs)
			return cls.create(**create_args)

	@classmethod
	def exists(cls, **kwargs):
		try:
			cls.find_one(**kwargs)
			return True
		except NoResultFound:
			return False

	@classmethod
	def _repr_class_template(cls):
		col_names = [col.name for col in cls.__table__.columns]
		item_format = '{col}={{obj.{col}!r}}'
		fields = ', '.join(item_format.format(col=col) for col in col_names)
		return '{class_name}({fields})'.format(
			class_name=cls.__name__,
			fields=fields,
			)

	def __repr__(self):
		class_template = self._repr_class_template()
		return class_template.format(obj=self)

	@classmethod
	def query_default_order(cls):
		"""Return a class query with a default order."""
		raise NotImplementedError

	@classmethod
	def _get_pkey_col(cls):
		primary_key_cols = inspect(cls).primary_key
		if len(primary_key_cols) != 1:
			msg = 'Class %s does not have exactly one primary key column' % cls
			raise NotImplementedError(msg)
		return primary_key_cols[0]

	@classmethod
	def fkey_constraint(cls, *args, ondelete='CASCADE', onupdate='CASCADE'):
		"""Return a ForeignKeyConstraint for the primary keys of this model."""
		pkey_col = cls._get_pkey_col()
		return ForeignKey(pkey_col, *args, ondelete=ondelete, onupdate=onupdate)

	@classmethod
	def pkey(cls, **kwargs):
		"""Return a Column definition for the primary key of this model."""
		pkey_col = cls._get_pkey_col()
		return foreign_key_col(pkey_col, **kwargs)

	def to_dict(self, sub=None):
		"""Create a dict of this obj's attributes and optionally related objects.

		Specify which relationships to include as keys in `sub`. The value of
		each key is the argument to pass to that relation's `to_dict`.

		For example:

		class Character(BaseModel):
			first_name = Column(String)
			last_name = Column(String)
			parents = relationship(Character)
			siblings = relationship(Character)

		`bart.to_dict({'parents': {'siblings': None}}) == {
			'first_name': 'Bart',
			'last_name': 'Simpson',
			'parents': [
				{
					'first_name': 'Homer',
					'last_name': 'Simpson',
					'siblings': [],
					},
				{
					'first_name': 'Marge',
					'last_name': 'Simpson',
					'siblings': [
						{
							'first_name': 'Patty',
							'last_name': 'Bouvier',
							},
						{
							'first_name': 'Selma',
							'last_name': 'Bouvier',
							},
						],
					},
				]
			}`
		"""
		instance_state = inspect(self)
		columns = instance_state.mapper.column_attrs
		out = {col.key: getattr(self, col.key) for col in columns}
		sub = sub or {}
		for relationship_name, args in sub.items():
			relationship = getattr(self, relationship_name)
			try:
				out[relationship_name] = relationship.to_dict(args)
			except AttributeError:
				if isinstance(relationship, (InstrumentedList, InstrumentedSet)):
					out[relationship_name] = []
					for relation in relationship:
						out[relationship_name].append(relation.to_dict(args))
				elif isinstance(relationship, InstrumentedDict):
					out[relationship_name] = {}
					for k, relation in relationship.items():
						out[relationship_name][k] = relation.to_dict(args)
				else:
					msg = "Don't know how to handle relationship of type {rel_type}".format(
						rel_type=type(relationship),
					)
					raise NotImplementedError(msg)
		return out

	@classmethod
	def _get_path(cls, path, directory):
		if path is None:
			path = '%s.csv' % cls.__tablename__
			if directory:
				path = os.path.join(directory, path)
		else:
			if directory:
				raise ValueError('Must not pass path and directory')
		return path

	@classmethod
	def merge_csv(cls, path=None, directory=None, io_wrapper=None):
		"""Load data from a csv file and merge into db.

		This is slower than import because orm objects are created.
		"""
		path = cls._get_path(path, directory)
		logger.info('Importing %s to %s', path, cls)
		with open(path, 'r', newline='') as infile:
			cls.merge_from_file(infile, io_wrapper=io_wrapper)

	@classmethod
	def import_csv(cls, path=None, directory=None, io_wrapper=None):
		"""Import data from a csv file."""
		path = cls._get_path(path, directory)
		logger.info('Importing %s to %s', path, cls)
		with open(path, 'r', newline='') as infile:
			cls.import_from_file(infile, io_wrapper=io_wrapper)

	@classmethod
	def export_csv(cls, path=None, directory=None, io_wrapper=None):
		"""Export data to csv file."""
		path = cls._get_path(path, directory)
		logger.info('Exporting %s to %s', cls, path)
		try:
			with open(path, 'r', newline='') as infile:
				reader = csv.DictReader(infile)
				fieldnames = reader.fieldnames
		except IOError:
			fieldnames = None
		with open(path, 'w', newline='') as outfile:
			cls.export_to_file(outfile, fieldnames=fieldnames, io_wrapper=io_wrapper)

	@classmethod
	def import_from_file(cls, infile, io_wrapper=None):
		logger.info('Importing to %s', cls)
		if io_wrapper:
			infile = io_wrapper(infile)
		reader = csv.DictReader(infile)
		# TODO try insert many (not on session)
		# http://stackoverflow.com/questions/25694234/bulk-update-in-sqlalchemy-core-using-where
		# db.session.bulk_insert_mappings(cls, reader)
		rows = list(reader)
		db.engine.execute(cls.__table__.insert(), rows)

	@classmethod
	def merge_from_file(cls, infile, io_wrapper=None):
		logger.info('Merging to %s', cls)
		if io_wrapper:
			infile = io_wrapper(infile)
		reader = csv.DictReader(infile)
		for row in reader:
			obj = cls(**row)
			cls.query.session.merge(obj)

	@classmethod
	def export_to_file(cls, outfile, fieldnames=None, io_wrapper=None):
		logger.info('Exporting %s', cls)
		if io_wrapper:
			outfile = io_wrapper(outfile)
		fieldnames = fieldnames or []
		for col in cls.__table__.columns:
			if col.name not in fieldnames:
				fieldnames.append(col.name)
		writer = csv.DictWriter(outfile, fieldnames, extrasaction='ignore')
		writer.writeheader()
		try:
			query = cls.query_default_order()
		except NotImplementedError:
			query = cls.query
		for obj in query:
			writer.writerow(obj.__dict__)


class IntegerPKey():

	id = Column(Integer, primary_key=True)

	@classmethod
	def _get_pkey_col(cls):
		return cls.id

	def __hash__(self):
		return self.id

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id

	@classmethod
	def query_default_order(cls):
		return cls.query.order_by(cls.id)


class AbbrPKey():

	abbr = Column(String, primary_key=True)

	@classmethod
	def _get_pkey_col(cls):
		return cls.abbr

	def __hash__(self):
		return hash(self.abbr)

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.abbr == other.abbr

	@classmethod
	def query_default_order(cls):
		return cls.query.order_by(cls.abbr)
