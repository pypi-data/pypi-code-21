import logging
from traceback import format_exc
from functools import wraps
from io import StringIO
from cgi import FieldStorage
from collections import OrderedDict
from triedict import triedict, KeyNotFound
from string import Template
from .template_plain import man, usage, ensure_bytes
from . import template_form
from .. import _bind
from .._util import stream
from ... import exceptions
from ...annotations import Flag, InputFile
from ...program import Program

logger = logging.getLogger(__name__)

def plain(program, debug=False):
    positionals_in_path = True # TODO Add a False option.

    if not isinstance(program, Program):
        program = Program(program)

    @_as_app(program, debug)
    def app(req, res):
        section, tail = _get_section_tail(program, req)
        function = program[section]
        function.require_help()
        if positionals_in_path:
            try:
                arguments = _args_kwargs(function, tail, _params(function, req))
            except exceptions.CouldNotParse as e:
                e.section = section
                raise e
        else:
            arguments = _no_tail(function, section, tail, req)

        if function.return_type:
            content_type = function.return_type.original
        else:
            logger.warning('%r does not have a return type, using application/octet-stream' % function)
            content_type = 'application/octet-stream'

        try:
            output = function.run('wsgi', arguments)
        except exceptions.ShowHelp as e:
            res.content_type = 'text/html; charset=UTF-8'
            res.app_iter = [man(program, e)]
        else:
            res.content_type = content_type
            if function.return_type and function.return_type.parsed.startswith('text/'):
                res.app_iter = stream(output)
            else:
                if isinstance(output, bytes):
                    res.app_iter = [output]
                else:
                    res.app_iter = ensure_bytes(output)
    return app

def form(program, debug=False,
         template: InputFile=StringIO(template_form.default_template),
         description=None, author=None):
    '''
    :type f: Program, callable, list, or dict
    :param f: The program to produce the interface
    :param str name: Name of the program, used for environment variable settings
        If it is ``None`` (the default), we attempt to get the name from the function.
    :param bool debug: Print errors and debugging information to web pages?
    :type template: File-like object
    :param template: Template file for form pages
    :rtype: function
    :returns: WSGI application
    '''
    if not isinstance(program, Program):
        program = Program(program)

    if description is None and set(program) == {()}:
        description = program[()].description
    tpl = Template(template.read())

    @_as_app(program, debug)
    def app(req, res):
        section, tail = _get_section_tail(program, req)
        function = program[section]
        arguments = _no_tail(function, section, tail, req)

        method = 'get' if _allow_get(function) else 'post'
        def render_form(message, output):
            main = template_form.form(function, method, arguments, message or '', output or '')
            res.content_type = 'text/html; charset=UTF-8'
            res.app_iter = [tpl.substitute(
                title=program.name or '',
                description=description or '',
                author=author or '',
                body=main,
            ).encode('utf-8')]

        if req.method == 'GET' and not req.GET:
            render_form(None, None)
        else:
            try:
                output = function.run('wsgi', arguments)
            except exceptions.CouldNotParse as e:
                res.status = 400
                output = None
                message = e.message
            except Exception:
                if debug:
                    res.status = 500
                    message = 'Internal server error'
                    output = format_exc()
                else:
                    raise
            else:
                message = None

            if function.return_type:
                res.content_type = function.return_type.original
                res.app_iter = ensure_bytes(output)
            else:
                render_form(message, output)
    return app

def _get_section_tail(program, req):
    if req.path_info == '/':
        section = tuple()
        tail = []
    else:
        section, tail = _bind.web_section(program, req.path_info.split('/')[1:])

    if not section in program:
        raise exceptions.CouldNotParse(section=section, message='No such page')
    return section, tail

def _allow_get(function):
    return all(param.allow_get for param in function.all_parameters())
def _params(function, req):
    return req.params if _allow_get(function) else req.POST

def _no_tail(function, section, tail, req):
    try:
        if 0 < len(tail):
            raise exceptions.CouldNotParse(message='Page not found')
        arguments = _just_kwargs(function, _params(function, req))
    except exceptions.CouldNotParse as e:
        e.section = section
        raise e
    return arguments

def _as_app(program, debug):
    try:
        from webob import Response, Request
    except ImportError:
        logger.error('WebOb is not installed; run this: pip install horetu[all]')
        import sys
        sys.exit(1)

    def decorator(inner_app):
        def app(environ, start_response):
            req = Request(environ)
            res = Response()
            logger.debug(req)

            try:
                res.status = 200
                inner_app(req, res)
            except exceptions.CouldNotParse as e:
                res.status = 404
                res.content_type = 'text/html; charset=UTF-8'
                res.app_iter = [usage(program, e)]
            except Exception:
                if debug:
                    res.status = 500
                    res.content_type = 'text/plain; charset=UTF-8'
                    res.app_iter = [format_exc().encode('utf-8')]
                else:
                    raise
            return res(environ, start_response)
        return app
    return decorator

def _args_kwargs(function, args, kwargs):
    arguments = _bind.positionals(function, args)
        
    keyword2_params = triedict({param.name: param for param in function.keyword2})
    for key, value in kwargs.items():
        try:
            p = keyword2_params[key]
        except KeyNotFound:
            raise exceptions.CouldNotParse('No such argument: %s' % key)
        else:
            if isinstance(p, Flag):
                value = Flag.YES
            if not p.name in arguments:
                arguments[p.name] = []
            arguments[p.name].append(value)
    return arguments

def _just_kwargs(function, post):
    arguments = OrderedDict()
    params = triedict({param.name: param for param in function.all_parameters()})
    for key, value in post.items():
        try:
            p = params[key]
        except KeyNotFound:
            raise exceptions.CouldNotParse('No such argument: %s' % key)
        else:
            if isinstance(p, Flag):
                value = Flag.YES
            if isinstance(value, FieldStorage) or value:
                if not p.name in arguments:
                    arguments[p.name] = []
                arguments[p.name].append(value)
    return arguments
