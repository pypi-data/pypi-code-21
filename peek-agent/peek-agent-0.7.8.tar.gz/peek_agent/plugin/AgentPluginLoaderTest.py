import logging

import sys
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.trial import unittest

from .AgentPluginLoader import agentPluginLoader

logger = logging.getLogger(__name__)

PLUGIN_NOOP = "plugin_noop"


class AgentPluginLoaderTest(unittest.TestCase):
    def testLoadAll(self):
        agentPluginLoader.loadCorePlugins()
        agentPluginLoader.loadOptionalPlugins()

        agentPluginLoader.startCorePlugins()
        agentPluginLoader.startOptionalPlugins()


        logger.info(agentPluginLoader.listPlugins())

        for plugin in list(agentPluginLoader._loadedPlugins.values()):
            logger.info("configUrl = %s", plugin.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d

    def testUnregister(self):
        loadedModuleBefore = set(sys.modules)

        agentPluginLoader.loadPlugin(PLUGIN_NOOP)
        self.assertTrue(PLUGIN_NOOP in sys.modules)

        agentPluginLoader.unloadPlugin(PLUGIN_NOOP)

        loadedModuleNow = set(sys.modules) - loadedModuleBefore

        # Ensure that none of the modules contain the plugin_name
        for modName in loadedModuleNow:
            self.assertFalse(PLUGIN_NOOP in modName)

    def testReRegister(self):
        agentPluginLoader.loadPlugin(PLUGIN_NOOP)
        agentPluginLoader.loadPlugin(PLUGIN_NOOP)

        for plugin in list(agentPluginLoader._loadedPlugins.values()):
            logger.info("configUrl = %s", plugin.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d
