#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the storage interface classes."""

import unittest

from plaso.storage import interface


class SerializedAttributeContainerListTets(unittest.TestCase):
  """Tests for the serialized attribute container list."""

  # pylint: disable=protected-access

  # TODO: add tests for number_of_attribute_containers property

  def testEmpty(self):
    """Tests the Empty function."""
    container_list = interface.SerializedAttributeContainerList()

    container_list.Empty()
    self.assertEqual(container_list._list, [])

    # TODO: improve test coverage.

  # TODO: add tests for GetAttributeContainerByIndex function
  # TODO: add tests for PopAttributeContainer function
  # TODO: add tests for PushAttributeContainer function


# TODO: add tests for BaseStorageFile
# TODO: add tests for StorageFileMergeReader
# TODO: add tests for StorageFileReader
# TODO: add tests for StorageWriter
# TODO: add tests for StorageFileWriter


if __name__ == '__main__':
  unittest.main()
