from __future__ import absolute_import

from .apiresource import ListObject
from .user import User
from .dataset import Dataset
from .datasetfield import DatasetField
from .datasetimport import DatasetImport
from .datasetexport import DatasetExport
from .datasetcommit import DatasetCommit
from .datasetmigration import DatasetMigration
from .datasettemplate import DatasetTemplate
from .vault_sync_task import VaultSyncTask
from .object_copy_task import ObjectCopyTask
from .manifest import Manifest
from .object import Object
from .vault import Vault
from .task import Task
from .beacon import Beacon
from .beaconset import BeaconSet


types = {
    'Beacon': Beacon,
    'BeaconSet': BeaconSet,
    'Dataset': Dataset,
    'DatasetImport': DatasetImport,
    'DatasetExport': DatasetExport,
    'DatasetCommit': DatasetCommit,
    'DatasetMigration': DatasetMigration,
    'DatasetTemplate': DatasetTemplate,
    'DatasetField': DatasetField,
    'Manifest': Manifest,
    'Object': Object,
    'ObjectCopyTask': ObjectCopyTask,
    'ECSTask': Task,
    'VaultSyncTask': VaultSyncTask,
    'User': User,
    'Vault': Vault,
    'list': ListObject
}
