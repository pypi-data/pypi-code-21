# -*- coding: utf-8 -*-
"""
Main datary sdk module
"""
import structlog

from .categories import DataryCategories
from .operations import (
    DataryAddOperation,
    DataryModifyOperation,
    DataryRenameOperation,
    DataryRemoveOperation,
    DataryCleanOperation,
    DataryOperationLimits,
)

from .commits import DataryCommits
from .datasets import (
    DataryDatasets)

from .members import DataryMembers
from .operations import (
    DataryOperations)

from . import version

logger = structlog.getLogger(__name__)
URL_BASE = "http://api.datary.io/"


class Datary(DataryCategories, DataryCommits, DataryMembers):
    """
    Datary main api class.
    Inherits from the rest of Datary modules its api functionality :
    - DataryAuth
    - DataryCategories
    - DataryCommits
    - DataryDatasets
    - DataryFiletrees
    - DataryMembers
    - DataryAddOperation
    - DataryRepos
    - DataryModifyOperation
    - DataryRemoveOperation
    """

    __version__ = version.__version__

    # Datary Entity Meta Field Allowed
    ALLOWED_DATARY_META_FIELDS = [
        "axisHeaders",
        "caption",
        "citation",
        "description",
        "dimension",
        "downloadUrl",
        "includesAxisHeaders",
        "lastUpdateAt",
        "period",
        "propOrder",
        "rootAleas",
        "size",
        "sha1",
        "sourceUrl",
        "summary",
        "title",
        "traverseOnly",
        "bigdata",
        "dimension"]


class DatarySizeLimitException(Exception):
    """
    Datary exception for size limit exceed
    """

    def __init__(self, msg='', src_path='', size=-1):
        super(DatarySizeLimitException, self).__init__(self, msg)
        self.msg = msg
        self.src_path = src_path
        self.size = size

    def __str__(self):
        return "{};{};{}".format(self.msg, self.src_path, self.size)
