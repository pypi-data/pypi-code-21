# -*- coding: utf-8 -*-
"""The preprocess plugins manager."""

from __future__ import unicode_literals

import logging

from dfvfs.helpers import file_system_searcher
from dfvfs.helpers import windows_path_resolver
from dfwinreg import interface as dfwinreg_interface
from dfwinreg import regf as dfwinreg_regf
from dfwinreg import registry as dfwinreg_registry
from dfwinreg import registry_searcher

from plaso.lib import errors
from plaso.preprocessors import interface


class FileSystemWinRegistryFileReader(dfwinreg_interface.WinRegistryFileReader):
  """A file system-based Windows Registry file reader."""

  def __init__(self, file_system, mount_point, environment_variables=None):
    """Initializes a Windows Registry file reader object.

    Args:
      file_system (dfvfs.FileSytem): file system.
      mount_point (dfvfs.PathSpec): mount point path specification.
      environment_variables (Optional[list[EnvironmentVariableArtifact]]):
          environment variables.
    """
    super(FileSystemWinRegistryFileReader, self).__init__()
    self._file_system = file_system
    self._path_resolver = self._CreateWindowsPathResolver(
        file_system, mount_point, environment_variables=environment_variables)

  def _CreateWindowsPathResolver(
      self, file_system, mount_point, environment_variables):
    """Create a Windows path resolver and sets the evironment variables.

    Args:
      file_system (dfvfs.FileSytem): file system.
      mount_point (dfvfs.PathSpec): mount point path specification.
      environment_variables (list[EnvironmentVariableArtifact]): environment
          variables.

    Returns:
      dfvfs.WindowsPathResolver: Windows path resolver.
    """
    if environment_variables is None:
      environment_variables = []

    path_resolver = windows_path_resolver.WindowsPathResolver(
        file_system, mount_point)

    for environment_variable in environment_variables:
      name = environment_variable.name.lower()
      if name not in ('systemroot', 'userprofile'):
        continue

      path_resolver.SetEnvironmentVariable(
          environment_variable.name, environment_variable.value)

    return path_resolver

  def _OpenPathSpec(self, path_specification, ascii_codepage='cp1252'):
    """Opens the Windows Registry file specified by the path specification.

    Args:
      path_specification (dfvfs.PathSpec): path specfication.
      ascii_codepage (Optional[str]): ASCII string codepage.

    Returns:
      WinRegistryFile: Windows Registry file or None.
    """
    if not path_specification:
      return

    file_entry = self._file_system.GetFileEntryByPathSpec(path_specification)
    if file_entry is None:
      return

    file_object = file_entry.GetFileObject()
    if file_object is None:
      return

    registry_file = dfwinreg_regf.REGFWinRegistryFile(
        ascii_codepage=ascii_codepage)

    try:
      registry_file.Open(file_object)
    except IOError as exception:
      logging.warning(
          'Unable to open Windows Registry file with error: {0:s}'.format(
              exception))
      file_object.close()
      return

    return registry_file

  def Open(self, path, ascii_codepage='cp1252'):
    """Opens the Windows Registry file specified by the path.

    Args:
      path (str): path of the Windows Registry file.
      ascii_codepage (Optional[str]): ASCII string codepage.

    Returns:
      WinRegistryFile: Windows Registry file or None.
    """
    path_specification = self._path_resolver.ResolvePath(path)
    if path_specification is None:
      return

    return self._OpenPathSpec(path_specification)


class PreprocessPluginsManager(object):
  """Preprocess plugins manager."""

  _plugins = {}
  _file_system_plugins = {}
  _registry_value_plugins = {}

  @classmethod
  def CollectFromFileSystem(
      cls, artifacts_registry, knowledge_base, searcher, file_system):
    """Collects values from Windows Registry values.

    Args:
      artifacts_registry (artifacts.ArtifactDefinitionsRegistry): artifacts
          definitions registry.
      knowledge_base (KnowledgeBase): to fill with preprocessing information.
      searcher (dfvfs.FileSystemSearcher): file system searcher to preprocess
          the file system.
      file_system (dfvfs.FileSystem): file system to be preprocessed.
    """
    for preprocess_plugin in cls._file_system_plugins.values():
      artifact_definition = artifacts_registry.GetDefinitionByName(
          preprocess_plugin.ARTIFACT_DEFINITION_NAME)
      if not artifact_definition:
        logging.warning('Missing artifact definition: {0:s}'.format(
            preprocess_plugin.ARTIFACT_DEFINITION_NAME))
        continue

      try:
        preprocess_plugin.Collect(
            knowledge_base, artifact_definition, searcher, file_system)
      except (IOError, errors.PreProcessFail) as exception:
        logging.warning((
            'Unable to collect value from artifact definition: {0:s} '
            'with error: {1:s}').format(
                preprocess_plugin.ARTIFACT_DEFINITION_NAME, exception))
        continue

  @classmethod
  def CollectFromWindowsRegistry(
      cls, artifacts_registry, knowledge_base, searcher):
    """Collects values from Windows Registry values.

    Args:
      artifacts_registry (artifacts.ArtifactDefinitionsRegistry): artifacts
          definitions registry.
      knowledge_base (KnowledgeBase): to fill with preprocessing information.
      searcher (dfwinreg.WinRegistrySearcher): Windows Registry searcher to
          preprocess the Windows Registry.
    """
    for preprocess_plugin in cls._registry_value_plugins.values():
      artifact_definition = artifacts_registry.GetDefinitionByName(
          preprocess_plugin.ARTIFACT_DEFINITION_NAME)
      if not artifact_definition:
        logging.warning('Missing artifact definition: {0:s}'.format(
            preprocess_plugin.ARTIFACT_DEFINITION_NAME))
        continue

      try:
        preprocess_plugin.Collect(knowledge_base, artifact_definition, searcher)
      except (IOError, errors.PreProcessFail) as exception:
        logging.warning((
            'Unable to collect value from artifact definition: {0:s} '
            'with error: {1:s}').format(
                preprocess_plugin.ARTIFACT_DEFINITION_NAME, exception))
        continue

  @classmethod
  def DeregisterPlugin(cls, plugin_class):
    """Deregisters an preprocess plugin class.

    Args:
      preprocess_plugin (type): preprocess plugin class.

    Raises:
      KeyError: if plugin class is not set for the corresponding name.
      TypeError: if the source type of the plugin class is not supported.
    """
    name = plugin_class.ARTIFACT_DEFINITION_NAME.lower()
    if name not in cls._plugins:
      raise KeyError(
          'Artifact plugin class not set for name: {0:s}.'.format(name))

    del cls._plugins[name]

    if name in cls._file_system_plugins:
      del cls._file_system_plugins[name]

    if name in cls._registry_value_plugins:
      del cls._registry_value_plugins[name]

  @classmethod
  def GetNames(cls):
    """Retrieves the names of the registered artifact definitions.

    Returns:
      list[str]: registered artifact definitions names.
    """
    return [
        plugin_class.ARTIFACT_DEFINITION_NAME
        for plugin_class in cls._plugins.values()]

  @classmethod
  def RegisterPlugin(cls, plugin_class):
    """Registers an preprocess plugin class.

    Args:
      plugin_class (type): preprocess plugin class.

    Raises:
      KeyError: if plugin class is already set for the corresponding name.
      TypeError: if the source type of the plugin class is not supported.
    """
    name = plugin_class.ARTIFACT_DEFINITION_NAME.lower()
    if name in cls._plugins:
      raise KeyError(
          'Artifact plugin class already set for name: {0:s}.'.format(name))

    preprocess_plugin = plugin_class()

    cls._plugins[name] = preprocess_plugin

    if isinstance(
        preprocess_plugin, interface.FileSystemArtifactPreprocessorPlugin):
      cls._file_system_plugins[name] = preprocess_plugin

    elif isinstance(
        preprocess_plugin,
        interface.WindowsRegistryValueArtifactPreprocessorPlugin):
      cls._registry_value_plugins[name] = preprocess_plugin

  @classmethod
  def RegisterPlugins(cls, plugin_classes):
    """Registers preprocess plugin classes.

    Args:
      plugin_classes (list[type]): preprocess plugin classses.

    Raises:
      KeyError: if plugin class is already set for the corresponding name.
    """
    for plugin_class in plugin_classes:
      cls.RegisterPlugin(plugin_class)

  @classmethod
  def RunPlugins(
      cls, artifacts_registry, file_system, mount_point, knowledge_base):
    """Runs the preprocessing plugins.

    Args:
      artifacts_registry (artifacts.ArtifactDefinitionsRegistry): artifacts
          definitions registry.
      file_system (dfvfs.FileSystem): file system to be preprocessed.
      mount_point (dfvfs.PathSpec): mount point path specification that refers
          to the base location of the file system.
      knowledge_base (KnowledgeBase): to fill with preprocessing information.
    """
    searcher = file_system_searcher.FileSystemSearcher(file_system, mount_point)

    cls.CollectFromFileSystem(
        artifacts_registry, knowledge_base, searcher, file_system)

    # Run the Registry plugins separately so we do not have to open
    # Registry files for every preprocess plugin.

    environment_variables = None
    if knowledge_base:
      environment_variables = knowledge_base.GetEnvironmentVariables()

    registry_file_reader = FileSystemWinRegistryFileReader(
        file_system, mount_point, environment_variables=environment_variables)
    win_registry = dfwinreg_registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    searcher = registry_searcher.WinRegistrySearcher(win_registry)

    cls.CollectFromWindowsRegistry(
        artifacts_registry, knowledge_base, searcher)

    if not knowledge_base.HasUserAccounts():
      logging.warning('Unable to find any user accounts on the system.')
