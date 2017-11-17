"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Nov 16, 2017

@author: jrm
"""
import re
from atom.api import Atom, List, Float, Unicode, set_default

from .bridge import JavaBridgeObject, JavaCallback, JavaMethod, JavaProxy
from .android_activity import Activity
from .app import AndroidApplication


class WifiManager(JavaBridgeObject):
    _instance = None
    __nativeclass__ = set_default('android.new.wifi.WifiManager')

    PERMISSIONS_REQUIRED = [
        'android.permission.ACCESS_COARSE_LOCATION',
        'android.permission.ACCESS_WIFI_STATE',
        'android.permission.CHANGE_WIFI_STATE'
    ]

    SCAN_RESULTS_AVAILABLE_ACTION = ''

    getScanResults = JavaMethod()
    setWifiEnabled = JavaMethod('boolean')
    isWifiEnabled = JavaMethod(returns='boolean')
    startScan = JavaMethod(returns='boolean')
    reassociate = JavaMethod(returns='boolean')
    reconnect = JavaMethod(returns='boolean')
    removeNetwork = JavaMethod('int', returns='boolean')


    @classmethod
    def instance(cls):
        """ Get an instance of this service if it was already requested.

        You should request it first using `WifiManager.get()`

        __Example__

            :::python

            def on_manager(m):
                #: Do stuff with it
                assert m == WifiManager.instance()

            WifiManager.get().then(on_manager)


        """
        if cls._instance:
            return cls._instance

    @classmethod
    def get(cls):
        """ Acquires the WifiManager service async. """

        app = AndroidApplication.instance()
        f = app.create_future()

        if cls._instance:
            app.set_future_result(f, cls._instance)
            return f

        def on_service(obj_id):
            #: Create the manager
            if not WifiManager.instance():
                m = WifiManager(__id__=obj_id)
            else:
                m = WifiManager.instance()
            app.set_future_result(f, m)

        app.get_system_service(Activity.WIFI_SERVICE).then(on_service)

        return f

    def __init__(self,*args, **kwargs):
        if WifiManager._instance is not None:
            raise RuntimeError("Only one instance of WifiManager can exist! "
                               "Use WifiManager.instance() instead!")
        super(WifiManager, self).__init__(*args, **kwargs)
        WifiManager._instance = self

    # -------------------------------------------------------------------------
    # Public api
    # -------------------------------------------------------------------------
    @classmethod
    def is_wifi_enabled(cls):
        """ Check if wifi is currently enabled.
        
        Returns
        --------
            result: future
              A future that resolves with the value.

        """
        app = AndroidApplication.instance()
        f = app.create_future()

        def on_ready(m):
            m.isWifiEnabled().then(f.set_result)

        WifiManager.get().then(on_ready)
        return f


    @classmethod
    def get_available_networks(cls):
        """ Get the wifi networks currently available.
        
        Returns
        --------
            result: future
                A future that resolves with the list of networks availabe.

        """
        app = AndroidApplication.instance()
        f = app.create_future()

        def on_ready(m):
            m.getScanResults().then(f.set_result)

        WifiManager.get().then(on_ready)
        return f

    # @classmethod
    # def stop(self):
    #     """ Stops location updates if currently updating.
    #
    #     """
    #     manager = WifiManager.instance()
    #     if manager:
    #         for l in manager.listeners:
    #             manager.removeUpdates(l)
    #         manager.listeners = []


    @classmethod
    def check_permission(cls):
        """ Returns a future that returns a boolean indicating if permission is
         currently granted or denied. If permission is denied, you can request 
         using `WifiManager.request_permission()` below.

        """
        app = AndroidApplication.instance()
        permission = WifiManager.PERMISSIONS_REQUIRED
        return app.has_permission(permission)

    @classmethod
    def request_permission(cls):
        """ Requests permission and returns an future result that returns a 
        boolean indicating if the permission was granted or denied.
         
        """
        app = AndroidApplication.instance()
        f = app.create_future()

        def on_result(perms):
            allowed = True
            for p in perms:
                allowed = allowed and perms[p]
            app.set_future_result(f, allowed)

        app.request_permissions(WifiManager.PERMISSIONS_REQUIRED).then(on_result)

        return f



    # def __del__(self):
    #     """ Remove any listeners before destroying """
    #     self.stop()
    #     super(WifiManager, self).__del__()

