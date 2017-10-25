import logging
from typing import Type, Tuple

import os
from twisted.internet.defer import inlineCallbacks

from peek_client.plugin.PeekClientPlatformHook import PeekClientPlatformHook
from peek_platform.frontend.NativescriptBuilder import NativescriptBuilder
from peek_platform.frontend.WebBuilder import WebBuilder
from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC

logger = logging.getLogger(__name__)


class ClientPluginLoader(PluginLoaderABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "ClientPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        PluginLoaderABC.__init__(self, *args, **kwargs)

    @property
    def _entryHookFuncName(self) -> str:
        return "peekClientEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginClientEntryHookABC

    @property
    def _platformServiceNames(self) -> [str]:
        return ["client"]

    @inlineCallbacks
    def loadOptionalPlugins(self):
        yield PluginLoaderABC.loadOptionalPlugins(self)

        from peek_platform import PeekPlatformConfig

        # --------------------
        # Prepare the Peek Mobile

        mobileProjectDir = None
        try:
            import peek_mobile
            mobileProjectDir = os.path.dirname(peek_mobile.__file__)

        except:
            pass

        if not mobileProjectDir:
            logger.warning("Skipping builds of peek-mobile"
                           ", the package can not be imported")

        else:
            nsBuilder = NativescriptBuilder(mobileProjectDir,
                                            "peek-mobile",
                                            PeekPlatformConfig.config,
                                            self._loadedPlugins.values())
            yield nsBuilder.build()

            mobileWebBuilder = WebBuilder(mobileProjectDir,
                                          "peek-mobile",
                                          PeekPlatformConfig.config,
                                          self._loadedPlugins.values())
            yield mobileWebBuilder.build()

        # --------------------
        # Prepare the Peek Desktop

        desktopProjectDir = None
        try:
            import peek_desktop
            desktopProjectDir = os.path.dirname(peek_desktop.__file__)

        except:
            pass

        if not desktopProjectDir:
            logger.warning("Skipping builds of peek-desktop"
                           ", the package can not be imported")

        else:
            desktopWebBuilder = WebBuilder(desktopProjectDir,
                                           "peek-desktop",
                                           PeekPlatformConfig.config,
                                           self._loadedPlugins.values())
            yield desktopWebBuilder.build()

    def unloadPlugin(self, pluginName: str):
        PluginLoaderABC.unloadPlugin(self, pluginName)

        # Remove the Plugin resource tree
        from peek_client.backend.SiteRootResource import mobileRoot
        try:
            mobileRoot.deleteChild(pluginName.encode())
        except KeyError:
            pass

        # Remove the Plugin resource tree
        from peek_client.backend.SiteRootResource import desktopRoot
        try:
            desktopRoot.deleteChild(pluginName.encode())
        except KeyError:
            pass

    @inlineCallbacks
    def _loadPluginThrows(self, pluginName: str,
                          EntryHookClass: Type[PluginCommonEntryHookABC],
                          pluginRootDir: str,
                          requiresService: Tuple[str, ...]) -> PluginCommonEntryHookABC:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekClientPlatformHook(pluginName)

        pluginMain = EntryHookClass(pluginName=pluginName,
                                    pluginRootDir=pluginRootDir,
                                    platform=platformApi)

        # Load the plugin
        yield pluginMain.load()

        # Add all the resources required to serve the backend site
        # And all the plugin custom resources it may create
        from peek_client.backend.SiteRootResource import mobileRoot
        mobileRoot.putChild(pluginName.encode(), platformApi.rootMobileResource)

        from peek_client.backend.SiteRootResource import desktopRoot
        desktopRoot.putChild(pluginName.encode(), platformApi.rootDesktopResource)

        self._loadedPlugins[pluginName] = pluginMain
