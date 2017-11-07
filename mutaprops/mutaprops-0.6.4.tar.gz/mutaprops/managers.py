#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import urllib.parse
from aiohttp import web, ClientSession, WSMsgType, WSServerHandshakeError,\
    ClientOSError
from .mutaprops import MutaPropError, MutaPropClass, MutaAction, MutaTypes
from collections import OrderedDict
import threading
import sockjs
import json
import logging
import os


class MutaManagerError(MutaPropError):
    pass


class HttpMutaManager(object):
    """
    Manages HTML5 gateway for controlling the MutaObjects.
    Each MutaObject is made accessible as REST API with websocket (SockJS)
    downstream channel for notifications about model update.

    Managers can be chained by specifying a "master manager"
    upon initialization. Master manager can see and manipulate the slave
    manager's MutaObjects.
    One Manager can have only one master, but can be master of many slaves.
    Chains can be of any length, but in practice the feasibility of long chains
    will be limited by the HTTP response times etc.
    """
    WEB_ASSETS = os.path.join(os.path.dirname(__file__), r"web_ui/dist/")
    INDEX_FILE = open(os.path.join(os.path.dirname(__file__),
                                   'web_ui', 'index.html'), 'rb').read()
    NOTIFICATION_PROPERTY_CHANGE = 'property_change'
    NOTIFICATION_EXTERNAL_CHANGE = 'external_change'
    NOTIFICATION_LOG_MESSAGE = 'log'
    NOTIFICATION_OBJECTS_CHANGE = 'objects_change'
    NOTIFICATION_TERMINATION = 'terminated'
    HEADER_SUPERVISOR = "muta-supervisor"
    EVENT_SOURCE_OBJECT = "object"
    EVENT_SOURCE_MASTER = "master"
    EVENT_SOURCE_USER = "user"

    class WsHandler(logging.Handler):
        """ Handler to forward logging messages over websocket."""

        def __init__(self, msg_callback, level=logging.NOTSET):
            self._msg_callback = msg_callback
            super().__init__(level)

        def emit(self, record):
            self._msg_callback(HttpMutaManager.NOTIFICATION_LOG_MESSAGE,
                               **record.__dict__)

    def __init__(self, name, loop=None, master=None, local_dir=None,
                 help_doc=None, proxy_log=None, log_level=logging.NOTSET):
        """
        :param name:  Name displayed in the UI top menu.

        Optional:

        :param loop:  Asyncio loop. If not specified, a new one will be created.

        :param master: ``http://masteraddr:port``
                       Address of the master controller.

        :param local_dir:  Path to the directory which will be made accessible
                           in the webserver as ``/local``

        :param help_doc:  String
                          A HTML code to be displayed in the help window.

        :param proxy_log:  A :class:`logging.Logger` instance to be forwarded to
                           the UI.

        :param log_level:  A log level to be displayed at the UI level.
        """
        self._name = name
        self._app = web.Application(loop=loop)
        self._muta_objects = OrderedDict()
        self._init_router(local_dir=local_dir)
        self._sockjs_manager = None
        self._logger = logging.getLogger(HttpMutaManager.__class__.__name__)
        self._manager_proxies = {}
        self._proxy_reconnector_task = None
        self._master_manager = master
        self._host_addr = None
        self._host_port = None
        self._proxy_logger = None
        self._help_doc = help_doc

        # Logging
        if proxy_log is None:
            # Get root logger
            self._proxy_logger = logging.getLogger()
        else:
            self._proxy_logger = proxy_log

        self._proxy_logger.addHandler(HttpMutaManager.WsHandler(
                            self._send_notification, log_level))

    @asyncio.coroutine
    def _get_app_name(self, request):
        return web.Response(text=self._name)

    @asyncio.coroutine
    def _get_help_doc(self, request):
        return web.Response(text=self._help_doc)

    @asyncio.coroutine
    def _get_object_list(self, request):

        # Don't know if it's better to return empty list or 204...
        # if not self._muta_objects:
        #     return web.HTTPNoContent() # No objects defined

        # temp = {'objects': [obj.muta_id for obj in self._muta_objects]}
        # temp = [obj.muta_id for obj in self._muta_objects]
        temp = list(self._muta_objects.keys())
        return web.json_response(temp)

    def _find_object(self, request):
        return self._muta_objects[request.match_info['obj_id']]

    @asyncio.coroutine
    def _get_object(self, request):
        try:
            obj = self._find_object(request)
            if isinstance(obj, HttpMutaObjectProxy):
                return (yield from obj.get_object())
            else:
                return web.json_response(obj.to_dict())
        except (KeyError, AssertionError):
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _get_props(self, request):
        try:
            temp_obj = self._find_object(request)
            if isinstance(temp_obj, HttpMutaObjectProxy):
                return (yield from temp_obj.get_props())
            else:
                temp_props = [prop.to_dict(obj=temp_obj)
                              for prop in temp_obj.props.values()]
                return web.json_response(temp_props)
        except (KeyError, AssertionError):
            return web.HTTPNotFound()

    def _find_prop(self, obj, request):
        return obj.props[request.match_info['prop_id']]

    @asyncio.coroutine
    def _get_prop(self, request):
        try:
            temp_obj = self._find_object(request)
            if isinstance(temp_obj, HttpMutaObjectProxy):
                return (yield from temp_obj.get_prop(
                    request.match_info['prop_id']))
            else:
                return web.json_response(
                    self._find_prop(temp_obj, request).to_dict(obj=temp_obj))
        except (KeyError, AssertionError):
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _get_prop_value(self, request):
        try:
            temp_obj = self._find_object(request)
            if isinstance(temp_obj, HttpMutaObjectProxy):
                return (yield from temp_obj.get_prop_value(
                    request.match_info['prop_id']))
            else:
                return web.json_response(
                    self._find_prop(temp_obj, request).__get__(temp_obj))
        except (KeyError, AssertionError):
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _set_prop_value(self, request):
        try:
            temp_obj = self._find_object(request)
            value = urllib.parse.parse_qs(request.query_string)['value'][0]
            if isinstance(temp_obj, HttpMutaObjectProxy):
                return (yield from temp_obj.set_prop_value(
                    request.match_info['prop_id'], value))
            else:
                temp_prop = self._find_prop(temp_obj, request)

                if not temp_prop.is_writeable():
                    return web.HTTPMethodNotAllowed(
                        'value', [], text="Property is read only.")

                # The setting of property itself
                value = MutaTypes.typecast(temp_prop.value_type, value)
                set_result = temp_prop.muta_set(temp_obj, value)

                # In case of this action being from master manager,
                # update the UI
                if self.HEADER_SUPERVISOR == request.headers:
                    self._property_change(temp_obj.muta_id, temp_prop.prop_id,
                                          value, self.EVENT_SOURCE_MASTER)
                else:
                    # The change was done by user on UI, we have to
                    # notify the other clients or master UIs
                    self._property_change(temp_obj.muta_id, temp_prop.prop_id,
                                          value, self.EVENT_SOURCE_USER)

                # TODO: This should translate muta_set validation result to
                # HTTP Resp.
                return web.json_response(set_result)
        except (KeyError, AssertionError):
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _set_prop_action(self, request):
        # TODO broadcast notification in case a "supervisor header" is present
        try:
            temp_obj = self._find_object(request)
            if isinstance(temp_obj, HttpMutaObjectProxy):
                return (yield from temp_obj.set_prop_action(
                    request.match_info['prop_id']))
            else:
                temp_prop = self._find_prop(temp_obj, request)
                if isinstance(temp_prop, MutaAction):
                    temp_prop.muta_call(temp_obj)
                    return web.HTTPOk()
                else:
                    return web.HTTPMethodNotAllowed(
                        "action", ['value', ],
                        text="Resource is not MutaAction.")
        except (KeyError, AssertionError):
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _register_remote_manager(self, request):
        data = yield from request.json()
        self._logger.debug("Registering remote manager %s" % data)
        remote_address = data.get('address', None)
        if remote_address:
            # Check for a loop (remote address is also own master)
            if remote_address == self._master_manager:
                raise MutaManagerError("Remote proxy address cannot be " +
                                       "the same as the master manager.")
            try:
                # Add manager to the list of proxies
                temp_man = HttpManagerProxy(remote_address)
                self._add_manager_proxy(temp_man)

                # Attach the manager
                yield from temp_man.attach(self)
                return web.HTTPOk()
            except MutaManagerError as e:
                return web.HTTPError(reason=str(e))
        else:
            return web.HTTPBadRequest()

    @asyncio.coroutine
    def _remote_manager_reconnector(self, period=10):
        """
        Periodically try to re-connect to remote managers which got reconnected.
        :param period:  [seconds] Time interval between reconnect attempts.
        """
        while True:
            yield from asyncio.sleep(10)
            for addr, proxy in self._manager_proxies.items():
                if (not proxy.is_attached) and (not proxy.is_being_removed):
                    self._logger.debug(
                        "Attempting reconnection to remote manager @ %s" % addr)
                    try:
                        yield from proxy.attach(self)
                    except Exception as e:
                        self._logger.debug("Reconnect failed with %s" % e)

    def _add_manager_proxy(self, proxy):
        if proxy.address not in self._manager_proxies:
            self._manager_proxies[proxy.address] = proxy
        else:
            raise MutaManagerError("Proxy already exists for that name.")

    def _is_master_connected(self):
        for addr, proxy in self._manager_proxies.items():
            if proxy.is_attached:
                return True

    @asyncio.coroutine
    def _remove_manager_proxy(self, proxy):
        temp = self._manager_proxies.pop(proxy.address)
        if temp:
            yield from temp.detach()

    def _sockjs_handler(self, msg, session):
        """ SockJS handler is now not doing anything because we onlu use
        SockJS for downstream.
        :param session:
        :return:
        """
        if msg.tp == sockjs.MSG_OPEN:
            self._sockjs_manager = session.manager
            # session.manager.broadcast("Someone joined.")
        elif msg.tp == sockjs.MSG_CLOSED:
            self._sockjs_manager = None
            # session.manager.broadcast("Someone left.")

    def _property_change(self, obj_id, prop_id, value,
                         event_source=EVENT_SOURCE_OBJECT):
        self._send_notification(self.NOTIFICATION_PROPERTY_CHANGE,
                                objId=obj_id, propId=prop_id, value=value,
                                eventSource=event_source)
        self._logger.debug("Property {0} changed value to {1} on {2}".format(
            obj_id, prop_id, value))

    def _send_notification(self, msg_type, **kwargs):
        temp = {'type': msg_type, 'params': kwargs}
        self._send_ws_message(temp)

    def _send_ws_message(self, msg):
        if self._sockjs_manager:
            self._sockjs_manager.broadcast(msg)

    def _index(self, request):
        return web.Response(body=self.INDEX_FILE, content_type='text/html')

    def _init_router(self, local_dir=None):
        self._app.router.add_get('/', self._index)
        self._app.router.add_static('/dist', self.WEB_ASSETS, show_index=True)

        if local_dir:
            self._app.router.add_static('/local', local_dir, show_index=True)

        self._app.router.add_get('/api/appname', self._get_app_name)
        self._app.router.add_get('/api/help', self._get_help_doc)
        self._app.router.add_get('/api/objects', self._get_object_list)
        self._app.router.add_get('/api/objects/{obj_id}', self._get_object)
        self._app.router.add_get('/api/objects/{obj_id}/props', self._get_props)
        self._app.router.add_get('/api/objects/{obj_id}/props/{prop_id}',
                                 self._get_prop)
        self._app.router.add_get('/api/objects/{obj_id}/props/{prop_id}/value',
                                 self._get_prop_value)
        self._app.router.add_put('/api/objects/{obj_id}/props/{prop_id}',
                                 self._set_prop_value)

        # http://programmers.stackexchange.com/questions/141410/restful-state-changing-actions
        self._app.router.add_put('/api/objects/{obj_id}/props/{prop_id}/action',
                                 self._set_prop_action)
        self._app.router.add_post('/api/remote', self._register_remote_manager)
        sockjs.add_endpoint(self._app, self._sockjs_handler, name='notifier',
                            prefix='/api/notifications/')

    def add_object(self, muta_object, obj_id=None):
        """ Add decorated object to the UI manager.

        :param muta_object: An instance of a class decorated with
                            :func:`~mutaprops.decorators.mutaprop_class`.

        Optional:

        :param obj_id: 'Id to be used for the added `muta_object`.
        """
        self._logger.debug("Adding object")

        # Somewhat unnecessarily complicated checking
        if not (isinstance(muta_object, MutaPropClass) or
                    isinstance(muta_object, HttpMutaObjectProxy)):
            raise MutaPropError("Object is not MutaClass instance.")

        if not muta_object.is_muta_ready() and obj_id is None:
            raise MutaPropError("MutaObject is not initialized. " +
                                "Provide obj_id or initialize externally.")

        if muta_object.is_muta_ready():
            if obj_id:
                muta_object.muta_init(obj_id, self._property_change)
            else:
                muta_object.muta_init(muta_object.muta_id,
                                      self._property_change)

        else:
            muta_object.muta_init(obj_id, self._property_change)

        # Check that we won't have two objects with the same id
        if muta_object.muta_id in self._muta_objects:
            raise MutaPropError(
                "MutaObject with id {0} is already registered.".format(
                    muta_object.muta_id))

        self._muta_objects[muta_object.muta_id] = muta_object
        self._send_notification(self.NOTIFICATION_OBJECTS_CHANGE,
                                objId=muta_object.muta_id, action='added')
        self._logger.debug("Added object %s" % muta_object.muta_id)

    def remove_object(self, muta_object):
        """ Remove object from the UI manager. (Causes object to disappear from
            the UI).

        :param muta_object: Object to be removed.
        """
        try:
            temp = self._muta_objects.pop(muta_object.muta_id)
            temp.muta_unregister()
            self._send_notification(self.NOTIFICATION_OBJECTS_CHANGE,
                                    objId=temp.muta_id, action='removed')
            self._logger.debug("Removed object %s" % temp.muta_id)
        except KeyError:
            raise MutaManagerError("Object is not managed.")

    @asyncio.coroutine
    def _on_shutdown(self, app):
        self._logger.debug("On Shutdown got called...")
        # Broadcast termination
        self._send_notification(self.NOTIFICATION_TERMINATION)
        # Close all proxies
        for addr, proxy in self._manager_proxies.items():
            self._remove_manager_proxy(proxy)
        # Stop the reconnector
        yield from self._proxy_reconnector_task.cancel()

        # Remove all objects
        objects_to_remove = list(self._muta_objects.values())
        for obj in objects_to_remove:
            self.remove_object(obj)

    @asyncio.coroutine
    def register_on_master(self, master_addr):
        # I know that it's not good to re-load session for single request,
        # but in this case it's so infrequent it doesn't matter
        temp_session = ClientSession(loop=self._app.loop)
        resp = yield from temp_session.post(master_addr + '/api/remote',
                            data=json.dumps({'address':
                            "http://{0}:{1}".format(self._host_addr,
                                                    self._host_port)}))
        if resp.status != 200:
            raise MutaManagerError("Couldn't register to the master")
        yield from temp_session.close()

    def _run(self, host='0.0.0.0', port='8080'):

        # http://aiohttp.readthedocs.io/en/stable/_modules/aiohttp/web.html?highlight=run_app

        handler = self._app.make_handler()
        self._app.on_shutdown.append(self._on_shutdown)
        # Task for proxy reconnector
        self._proxy_reconnector_task = asyncio.async(
            self._remote_manager_reconnector(), loop=self._app.loop)

        # Now run it all
        self._host_addr = host
        self._host_port = port

        if self._master_manager:
            asyncio.async(self.register_on_master(self._master_manager),
                                  loop=self._app.loop)
        print("Server starting at http://{0}:{1}".format(host, port))
        self._app.loop.run_until_complete(asyncio.gather(
            self._app.loop.create_server(handler, host, port),
            self._proxy_reconnector_task))
        # self._app.loop.run_forever()

    def run(self, **aiohttp_kwargs):
        """ Run the manager.

        :param aiohttp_kwargs: HTTP server parameters as defined for aiohttp
                               `web.run_app <http://aiohttp.readthedocs.io/en/stable/web_reference.html#aiohttp.web.run_app>`_
        """
        # loop.run_forever()
        # web.run_app(self._app, **aiohttp_kwargs)
        self._run(**aiohttp_kwargs)

    def run_in_thread(self, **aiohttp_kwargs):
        """ Run the UI manager in a separate thread.

        Theoretically this allows to run the UI for code which is otherwise
        incompatible with Asyncio. In practice, this is a minefield and it was
        never properly tested.

        :param aiohttp_kwargs: HTTP server parameters as defined for aiohttp
                               `web.run_app <http://aiohttp.readthedocs.io/en/stable/web_reference.html#aiohttp.web.run_app>`_
        """
        t = threading.Thread(target=self._run, kwargs=aiohttp_kwargs)
        t.start()

    def shutdown(self):
        self._logger.debug("Shutting down the HttpManager...")
        self._app.shutdown()


class HttpManagerProxy:
    """
    Utility class representing a remote (slave) HTTP manager.
    """
    def __init__(self, address):
        self._address = address
        self._session = None
        self._logger = logging.getLogger(self.__class__.__name__)
        self._registered_objects = {}
        self._host_manager = None
        self._is_attached = False
        self._ws = None
        self._ws_man = None
        self._is_being_removed = False

    @property
    def session(self):
        return self._session

    @property
    def is_attached(self):
        return self._is_attached

    @property
    def address(self):
        return self._address

    @property
    def is_being_removed(self):
        """
        Host manager checks the flag to know if it shall try to reconnect
        with the remote manager.
        """
        return self._is_being_removed

    def _add_remote_object(self, obj):
        obj_proxy = HttpMutaObjectProxy(self, obj)
        try:
            self._host_manager.add_object(obj_proxy)
        except MutaPropError:
            # The object may already be there sometimes
            pass
        self._registered_objects[obj_proxy.muta_id] = obj_proxy

    def _remove_remote_object(self, obj):
        obj_proxy = self._registered_objects.pop(obj, None)
        if obj_proxy:
            self._host_manager.remove_object(obj_proxy)


    @asyncio.coroutine
    def attach(self, host_manager):
        """
        Attaches itself to the host manager, by making it's own remote
        MutaObjects part of the host managers object list.
        Also manages WebSocket connection to the remote manager and
        relays the messagest to the host manager.

        :param host_manager:  A host HttpMutaManager object.
        :return:
        """
        self._host_manager = host_manager
        self._session = ClientSession(loop=self._host_manager._app.loop)

        # Open the WebSocket
        try:
            addr = self._address + '/api/notifications/websocket'
            self._ws = yield from self._session.ws_connect(addr)
            self._logger.debug("Opened websocket at %s" % addr)
        except WSServerHandshakeError:
            raise MutaManagerError("Cannot establish WS connection to %s" %
                                   self._address)

        # Start the WS manager
        self._ws_man = asyncio.async(self.ws_manager(), loop=self._session.loop)

        # Get and process the remote objects
        resp = yield from self._session.get(self._address + '/api/objects')

        if resp.status != 200:
            raise MutaManagerError("Cannot access remote objects at %s" %
                                   self._address)

        objects = (yield from resp.json()) or []

        for obj in objects:
            self._add_remote_object(obj)

        self._is_attached = True
        self._logger.debug("Remote manager %s attached." % self._address)

    @asyncio.coroutine
    def detach(self):
        if self.is_attached:
            self._logger.debug("Detaching remote manager %s" % self._address)
            for id, obj in self._registered_objects.items():
                self._host_manager.remove_object(obj)

            # Just to be sure
            self._registered_objects = {}

            # Disconnect the WS manager
            self._ws_man.cancel()

            # Close the websocket and session
            yield from self._ws.close()
            yield from self._session.close()

            # Tell host manager that it's detached
            # self._host_manager._on_proxy_manager_detach(self)

            self._is_attached = False

    @asyncio.coroutine
    def _disconnected(self):
        yield from self.detach()

    @asyncio.coroutine
    def ws_manager(self):
        """
        Coroutine implementing the Websocket communication task.
        """
        self._logger.debug("Starting WS manager for remote")
        while True:
            try:
                msg = yield from self._ws.receive()
                self._logger.debug("Received ws msg %s" % str(msg))
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    cmd = data.get('type')
                    if cmd == HttpMutaManager.NOTIFICATION_TERMINATION:
                        self._is_being_removed = True
                        yield from self._host_manager._remove_manager_proxy(self)

                    elif cmd == HttpMutaManager.NOTIFICATION_OBJECTS_CHANGE:
                        params = data.get('params', {})
                        action = params.get('action')

                        if action == 'added':
                            self._add_remote_object(params['objId'])
                        elif action == 'removed':
                            self._remove_remote_object(params['objId'])

                    self._logger.debug("Relaying wsmessage: %s" % str(data))
                    self._host_manager._send_ws_message(data)

                elif msg.type == WSMsgType.CLOSED:
                    self._logger.debug("Websocket closed: %s" % msg.data)
                    yield from self._disconnected()
                    break

                elif msg.type == WSMsgType.ERROR:
                    self._logger.debug("Websocket error: %s" % msg.data)
                    yield from self._disconnected()
                    break
            except Exception as e:
                self._logger.exception("WS manager error")
                break

        self._logger.debug("WS manager finished.")


class HttpMutaObjectProxy:
    """
    Utility class proxying remote MutaObjects through REST calls.
    """
    def __init__(self, manager_proxy, obj_id):
        self._manager_proxy = manager_proxy
        self._address = "{0}/api/objects/{1}".format(
            self._manager_proxy.address, obj_id)
        self._obj_id = obj_id
        self._session = self._manager_proxy.session

    # For MutaClass type object compatibility
    def is_muta_ready(self):
        return True

    def muta_unregister(self):
        pass

    def muta_init(self, object_id, change_callback=None):
        pass

    @property
    def muta_id(self):
        return self._obj_id

    @asyncio.coroutine
    def _get_resource(self, resource_address):
        try:
            if not self._manager_proxy.is_attached:
                raise MutaManagerError("Remote manager is not attached.")
            resp = yield from self._session.get(self._address +
                                                resource_address)
            temp = yield from resp.text()
            return web.json_response(text=temp)
        except (ClientOSError, MutaManagerError) as e:
            return web.HTTPNotFound(text=str(e))

    @asyncio.coroutine
    def _put_resource(self, resource_address):
        try:
            if not self._manager_proxy.is_attached:
                raise MutaManagerError("Remote manager is not attached.")
            # Add header saying it's from supervisor manager
            resp = yield from self._session.put(self._address +
                resource_address,
                headers={HttpMutaManager.HEADER_SUPERVISOR: 'true'})
            text = yield from resp.text()
            return web.json_response(status=resp.status, text=text)
        except (ClientOSError, MutaManagerError) as e:
            return web.HTTPNotFound(text=str(e))
    @asyncio.coroutine
    def get_object(self):
        return (yield from self._get_resource(''))

    @asyncio.coroutine
    def get_props(self):
        return (yield from self._get_resource('/props'))

    @asyncio.coroutine
    def get_prop(self, prop_id):
        return (yield from self._get_resource('/props/{0}'.format(prop_id)))

    @asyncio.coroutine
    def get_prop_value(self, prop_id):
        return (yield from self._get_resource('/props/{0}/value'
                                              .format(prop_id)))

    @asyncio.coroutine
    def set_prop_value(self, prop_id, value):
        return (yield from self._put_resource('/props/{0}?value={1}'
                                              .format(prop_id, value)))

    @asyncio.coroutine
    def set_prop_action(self, prop_id):
        return (yield from self._put_resource('/props/{0}/action'
                                              .format(prop_id)))
