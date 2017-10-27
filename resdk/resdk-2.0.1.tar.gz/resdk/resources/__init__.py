""".. Ignore pydocstyle D400.

=========
Resources
=========

Resource classes
================

.. autoclass:: resdk.resources.base.BaseResource
   :members:

.. autoclass:: resdk.resources.Data
   :members:

.. autoclass:: resdk.resources.collection.BaseCollection
   :members:

.. autoclass:: resdk.resources.Collection
   :members:

.. autoclass:: resdk.resources.Sample
   :members:

.. autoclass:: resdk.resources.Relation
   :members:

.. autoclass:: resdk.resources.Process
   :members:

.. autoclass:: resdk.resources.User
   :members:

Utility functions
=================

.. automodule:: resdk.resources.utils
   :members: iterate_fields, iterate_schema, find_field, fill_spaces,
       get_collection_id, get_data_id, get_sample_id, get_process_id

"""

from .collection import Collection
from .data import Data
from .descriptor import DescriptorSchema
from .process import Process
from .relation import Relation
from .sample import Sample
from .user import Group, User

__all__ = ('Collection', 'Data', 'Group', 'Sample', 'Process', 'Relation', 'User')
