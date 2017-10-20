# -*- coding: utf-8 -*-
"""The Elastic Search output module CLI arguments helper."""

from __future__ import unicode_literals

import getpass

from uuid import uuid4

from plaso.lib import errors
from plaso.cli.helpers import interface
from plaso.cli.helpers import manager
from plaso.cli.helpers import server_config
from plaso.output import elastic


class ElasticSearchServerArgumentsHelper(server_config.ServerArgumentsHelper):
  """Elastic Search server CLI arguments helper."""

  _DEFAULT_SERVER = '127.0.0.1'
  _DEFAULT_PORT = 9200


class ElasticSearchOutputArgumentsHelper(interface.ArgumentsHelper):
  """Elastic Search output module CLI arguments helper."""

  NAME = 'elastic'
  CATEGORY = 'output'
  DESCRIPTION = 'Argument helper for the Elastic Search output module.'

  _DEFAULT_INDEX_NAME = uuid4().hex
  _DEFAULT_DOC_TYPE = 'plaso_event'
  _DEFAULT_FLUSH_INTERVAL = 1000
  _DEFAULT_RAW_FIELDS = False
  _DEFAULT_ELASTIC_USER = None

  @classmethod
  def AddArguments(cls, argument_group):
    """Adds command line arguments the helper supports to an argument group.

    This function takes an argument parser or an argument group object and adds
    to it all the command line arguments this helper supports.

    Args:
      argument_group (argparse._ArgumentGroup|argparse.ArgumentParser):
          argparse group.
    """
    argument_group.add_argument(
        '--index_name', dest='index_name', type=str, action='store',
        default=cls._DEFAULT_INDEX_NAME, help=(
            'Name of the index in ElasticSearch.'))
    argument_group.add_argument(
        '--doc_type', dest='doc_type', type=str,
        action='store', default=cls._DEFAULT_DOC_TYPE, help=(
            'Name of the document type that will be used in ElasticSearch.'))
    argument_group.add_argument(
        '--flush_interval', dest='flush_interval', type=int,
        action='store', default=cls._DEFAULT_FLUSH_INTERVAL, help=(
            'Events to queue up before bulk insert to ElasticSearch.'))
    argument_group.add_argument(
        '--raw_fields', dest='raw_fields', action='store_true',
        default=cls._DEFAULT_RAW_FIELDS, help=(
            'Export string fields that will not be analyzed by Lucene.'))
    argument_group.add_argument(
        '--elastic_user', dest='elastic_user', action='store',
        default=cls._DEFAULT_ELASTIC_USER, help=(
            'Username to use for Elasticsearch authentication.'))

    ElasticSearchServerArgumentsHelper.AddArguments(argument_group)

  # pylint: disable=arguments-differ
  @classmethod
  def ParseOptions(cls, options, output_module):
    """Parses and validates options.

    Args:
      options (argparse.Namespace): parser options.
      output_module (OutputModule): output module to configure.

    Raises:
      BadConfigObject: when the output module object is of the wrong type.
      BadConfigOption: when a configuration parameter fails validation.
    """
    if not isinstance(output_module, elastic.ElasticSearchOutputModule):
      raise errors.BadConfigObject(
          'Output module is not an instance of ElasticSearchOutputModule')

    index_name = cls._ParseStringOption(
        options, 'index_name', default_value=cls._DEFAULT_INDEX_NAME)
    doc_type = cls._ParseStringOption(
        options, 'doc_type', default_value=cls._DEFAULT_DOC_TYPE)
    flush_interval = cls._ParseNumericOption(
        options, 'flush_interval', default_value=cls._DEFAULT_FLUSH_INTERVAL)
    raw_fields = getattr(
        options, 'raw_fields', cls._DEFAULT_RAW_FIELDS)
    elastic_user = cls._ParseStringOption(
        options, 'elastic_user', default_value=cls._DEFAULT_ELASTIC_USER)

    if elastic_user is not None:
      elastic_password = getpass.getpass(
          'Enter your Elasticsearch password: ')
    else:
      elastic_password = None

    ElasticSearchServerArgumentsHelper.ParseOptions(options, output_module)
    output_module.SetIndexName(index_name)
    output_module.SetDocType(doc_type)
    output_module.SetFlushInterval(flush_interval)
    output_module.SetRawFields(raw_fields)
    output_module.SetElasticUser(elastic_user)
    output_module.SetElasticPassword(elastic_password)


manager.ArgumentHelperManager.RegisterHelper(ElasticSearchOutputArgumentsHelper)
