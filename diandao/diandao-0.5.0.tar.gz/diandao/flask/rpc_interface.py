# -*- coding: utf-8 -*-
from importlib import import_module
from pkgutil import walk_packages
from flask import Blueprint, request
from diandao import JSON
from diandao.flask import app
from sys import exc_info
import inspect
import interfaces

blueprint = Blueprint('rpc', 'rpc')

for loader, name, is_pkg in walk_packages(interfaces.__path__):
    import_module(interfaces.__name__ + '.' + name)
    interface_module = getattr(interfaces, name)
    setattr(interfaces, name, getattr(interface_module, name))

# interface caches
_caches = {}

@blueprint.route('/rpc/<string:interface>/<string:method>', methods=["POST", "GET"])
def rpc(interface, method):
    if not interface or not method:
        return error_404(interface, method)
    interface = "%sInterface" % interface
    intf = None
    # 缓存接口实例, 避免多次创建
    if hasattr(_caches, str(interface).lower()):
        intf = _caches[str(interface).lower()]
    if intf is None and hasattr(interfaces, interface):
        intf = getattr(interfaces, interface)()
        _caches[str(interface).lower()] = intf

    # 无接口类
    if intf is None:
        return error_404(interface, method)

    # 接口无指定方法
    if not hasattr(intf, method):
        return error_404(interface, method)

    callee = getattr(intf, method)

    if not callable(callee):
        return error_404(interface, method)

    params = []
    data = None
    error = None

    try:
        params = get_params()
    except ValueError, e:
        # params参数解析异常
        error = {
            "code": 501,
            "message": "params parse error:%s" % e
        }
        return rpc_response(data, error=error)

    try:
        # 数组参数
        if isinstance(params, list):
            data = callee(*params)
        # kwargs 参数
        if isinstance(params, dict):
            data = callee(**params)
    except Exception, e:
        info = exc_info()
        errtype = info[0].__name__
        message = info[1].message
        trace = get_exc_traceback(info[2])
        error = {
            "code": 500,
            "message": "%s: %s on %s at line %s" % (errtype, message, trace['file'], trace['line'])
        }
        # 发送异常给app处理
        app.do_teardown_appcontext(info[1])
        # xloger 兼容
        if app.config.get('XLOGER_ENABLED', False):
            from xloger import xloger
            xloger.show_error(errtype, message, trace['file'], trace['line'])

    finally:
        return rpc_response(data, error=error)


def rpc_response(data, error=None, status=200):
    return JSON.stringify({
        "status": status,
        "error": error,
        "data": data
    })


def get_params():
    """获取请求中的params参数"""
    ps = request.values.get('params', type=str, default="[]")
    ps = JSON.parse(ps)
    return ps


def error_404(interface='', method=''):
    error = {
        "code": 404,
        "message": "Undefined Interface:%s.%s()" % (interface, method)
    }
    return rpc_response(None, error=error, status=404)


def get_exc_traceback(trace):
    if hasattr(trace, "tb_next") and trace.tb_next:
        return get_exc_traceback(trace.tb_next)

    trace = {
        "line": trace.tb_lineno,
        "file": inspect.getfile(trace.tb_frame)
    }
    return trace
