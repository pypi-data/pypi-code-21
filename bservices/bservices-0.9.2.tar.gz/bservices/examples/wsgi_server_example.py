# coding: utf-8
"""
WSGI Server
    Run:
        python -m bservices.examples.example_server

HTTP Client:
    Add:
        curl http://127.0.0.1:10000/set_data -d '{"data": "test_data"}' \
             -H "Content-Type: application/json"
        >>> {"id": 1}
    Get:
        curl http://127.0.0.1:10000/get_data?id=1
        >>> {"data": "test_data", "id": 1}

Restriction of `bservices.wsgi.Resource`:
    (1) Only support three kinds of Content-Type:
        A. text/plain
        B. application/json
        C. application/xml
    (2) Automatically serialize and deserialize the body of the request,
        but only for application/json, text/plain. If you want to receive and
        handle the XML content, you MUST register the serializer and deserializer
        of XML; or, it will raise a exception.

Controller Action API:
    If using the wrapper of `Resource`, you obey the action rules below.
    Or, you MUST implement the engine to handle the HTTP request.

    The logic of `Resource` is simply.
    1. It gets the controller, the action method, the URL pattern argument
       by the result that `routes` parsed.
    2. deserialize the body, if any.
    3. pass all the arguments to the action method and call it.
    4. handle the result.

    Handle the result the action method returned:
    (1) if a dict, serialize it to JSON.
    (2) if a object of bservices.wsgi.ResponseObject, serialize it by default.
    (3) If any others, hand it to webob.dec.wsgify to handle.

    In the meanwhile, it also handle some convenient functions, such as the
    default status code, see `bservices.wsgi.Resource._process_stack` and
    `bservices.wsgi.response`. Moreover, it support the action mapping and the
    extensions.

    Action API:
        Args:
            (1) MUST have a argument, req, which is a object of
                `bservices.wsgi.Request`.
            (2) Arguments that `routes` parsed will be past to the action method.
            (3) If having a body, the action method MUST supply a argument, body.

        Return:
            (1) a dict object
            (2) a bservices.wsgi.ResponseObject object
            (3) a exception based on webob.exc.HTTPException or
                bservices.exception.ExceptionBase, or
                bservices.exception.ConvertedException.
            (4) a object of webob.exc.HTTPException, or
                bservices.exception.ConvertedException, or their subclass.
            (5) any object compatible with webob.dec.wsgify.__call__, for
                example, None, string(str, bytes, unicode), webob.Response, etc.

            Notice:
                The first two will be serialized.
                see bservices.wsgi.ResponseObject.

Middleware:
    Method One:
        >>> app = API()
        >>> app = Middleware3(app)
        >>> app = Middleware2(app)
        >>> app = Middleware1(app)

    Method Two:
        >>> from bservices.middleware import get_app
        >>> middlewares = ["PATH.TO.Middleware1", "PATH.TO.Middleware2",
                           "PATH.TO.Middleware3"]
        >>> app = API()
        >>> app = get_app(app, middlewares)

    def get_app(app, middlewares, **kwargs):
        `middlewares` is a list or tuple object, whose elements are a str or
        the Middleware class. Moreover, `kwargs` may pass the Middleware class
        as the second argument, which is a dict.

Decorators:
    bservices.wsgi carries some convenient decorators to implement some
    functions rapidly.

    These decorators are used on the action method of the controller.

    @serializers(**serializers)
        Assign the some serializers for the action method.

    @deserializers(**deserializers)
        Assign the some deserializers for the action method.

    @response(code)
        Assign the default status code for the action method.

    @action(name)
        Assign the action name for the action method.

    Notice:
        bservices.wsgi.Resource supplies two pairs of serializers and
        deserializers, that's, JSON and TEXT. The serializers of JSON and TEXT
        are JSONDeserializer and TextDeserializer, and the deserializers of JSON
        and TEXT are JSONDictSerializer and TextSerializer. Certianly, you can
        assign yourself serializers and deserializers to replace them.

        The serializers and the deserializers only serialize the body of the
        request, or deserialize the body of the response.

    For their usage examples, see below.
"""
import logging
import multiprocessing

import routes
import eventlet
from oslo_config import cfg
from oslo_log import log
from oslo_service import service
from oslo_service.wsgi import Router

from bservices import wsgi, exception
from bservices.contrib.server import WSGIServer
from bservices.examples.db import api

LOG = logging.getLogger()
CONF = cfg.CONF

cli_opts = [
    cfg.StrOpt("listen_ip", default='0.0.0.0'),
    cfg.IntOpt("listen_port", default=10000)
]
CONF.register_cli_opts(cli_opts)


class DataController(wsgi.Controller):
    @wsgi.serializers(json=wsgi.JSONDictSerializer)
    @wsgi.deserializers(json=wsgi.JSONDeserializer)
    @wsgi.response(200)
    @wsgi.action("index")
    def get_data(self, req):
        try:
            id = int(req.GET["id"])
        except (KeyError, TypeError, ValueError):
            raise exception.BadRequest()

        ret = api.get_data(id)
        if not ret:
            raise exception.NotFound()
        return ret

    def set_data(self, req, body):
        try:
            data = body["data"]
        except (KeyError, TypeError, ValueError):
            raise exception.BadRequest()

        return api.set_data(data)


class API(Router):
    def __init__(self):
        mapper = routes.Mapper()
        mapper.redirect("", "/")

        resource = wsgi.Resource(DataController())
        mapper.connect("/get_data",
                       controller=resource,
                       action="get_data",
                       conditions={"method": ['GET']})
        mapper.connect("/set_data",
                       controller=resource,
                       action="set_data",
                       conditions={"method": ["POST"]})

        super(API, self).__init__(mapper)


def main(project="example"):
    log.register_options(CONF)
    # log.set_defaults(default_log_levels=None)
    CONF(project=project)

    log.setup(CONF, project)
    eventlet.monkey_patch(all=True)

    server = WSGIServer(CONF, project, API(), host=CONF.listen_ip,
                        port=CONF.listen_port, use_ssl=False, max_url_len=1024)
    launcher = service.launch(CONF, server, workers=multiprocessing.cpu_count())
    launcher.wait()


if __name__ == '__main__':
    main()
