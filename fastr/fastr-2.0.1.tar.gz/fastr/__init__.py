# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" FASTR is a top level package which includes all parts required to create
networks and edit networks.

.. class:: Network

    The class representing a Network, this is in fact a reference to
    :py:class:`fastr.core.network.Network`.

.. class:: NodeRun

    The class representing a NodeRun, this is in fact a reference to
    :py:class:`fastr.core.node.NodeRun`.

.. class:: Link

    The class representing a Link, this is in fact a reference to
    :py:class:`fastr.core.link.Link`.

.. class:: SourceNodeRun

    The class representing a data source, this is in fact a reference to
    :py:class:`fastr.core.node.SourceNodeRun`.

.. class:: SinkNodeRun

    The class representing a data sink, this is in fact a reference to
    :py:class:`fastr.core.node.SinkNodeRun`.

.. class:: ConstantNodeRun

    The class representing a constant data source, this is in fact a reference
    to :py:class:`fastr.core.node.ConstantNodeRun`.

.. data:: toollist

    A :py:class:`fastr.core.toolmanager.ToolManager` containing all Tools known
    to the FASTR environment. The toollist can be accessed in a similar way to
    a dict. Indexing with a tool id will return the newest version of the Tool.
    If a specific version of the tool is required a tuple can be used as the
    index:

    .. code-block:: python

        >>> import fastr
        >>> fastr.toollist['testtool']
        <Tool: testtool version: 4.2>
        >>> fastr.toollist['testtool', '2.0']
        <Tool: testtool version: 2.0>


.. data:: typelist

    A :py:class:`fastr.core.datatypemanager.DataTypeManager` containing all
    Types known to the FASTR environment. This is usuable as a dict where
    the key is the datatype id and the value is the datatype itself.
"""

# In the top level module we want to add some variables which are constants
# but use a non-constant name (not caps)
# pylint: disable=invalid-name

from colorama import init
init()

from fastr.configmanager import Config

# Get version info
from fastr import version
__version__ = version.version

#: Configuration of the fastr system
config = Config()

# Reference the logger object from the config
log = config.log

__all__ = ['Network', 'Link', 'Node', 'ConstantNode', 'SourceNode', 'SinkNode',
           'typelist', 'datatypes', 'plugins', 'toollist', 'networklist',
           'ioplugins', 'vfs']

# Import all fastr components
from fastr.core.network import Network
from fastr.core.link import Link
from fastr.core.node import Node
from fastr.core.node import ConstantNode
from fastr.core.node import SourceNode
from fastr.core.node import SinkNode

from fastr.core.pluginmanager import LazyModule, PluginManager
from fastr.core.datatypemanager import typelist
from fastr.core.vfs import VirtualFileSystem

# Import datatypes and create a lazy loading module for that
import fastr.datatypes
datatypes = LazyModule("datatypes", parent=fastr.datatypes, plugin_manager=typelist)

plugin_manager = PluginManager()
import fastr.plugins
plugins = LazyModule("plugins", parent=fastr.plugins, plugin_manager=plugin_manager)

from fastr.core.interface import InterfacePluginManager
from fastr.core.ioplugin import IOPluginManager
from fastr.core.target import TargetManager
from fastr.execution.executionpluginmanager import ExecutionPluginManager
from fastr.execution.networkrun import NetworkRun

# Load resource managers
from fastr.core.toolmanager import toollist
from fastr.core.networkmanager import networklist

# The following loads all ioplugins from the resources folder and registers the built-in vfs with the plugin list
ioplugins = IOPluginManager()
vfs = VirtualFileSystem()
execution_plugins = ExecutionPluginManager()
targets = TargetManager()

# Register the val URL for Python version under 2.7.3
ioplugins.register_url_scheme('val')
interfaces = InterfacePluginManager()

log.debug('Finished with the FASTR environment set up')


# Warn if this is not a neatly installed package from the stable branch
if fastr.config.warn_develop:
    if version.not_default_branch or version.from_mercurial:
        fastr.log.warning('Not running in a production installation (branch "{}" from {})'.format(
            version.hg_branch,
            'source code' if version.from_mercurial else 'installed package'
        ))
