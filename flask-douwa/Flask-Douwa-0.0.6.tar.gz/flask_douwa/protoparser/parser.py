# -*- coding=utf8 -*-
import logging
import os
import types
from ply import (
    yacc,
    lex,
)
from google.protobuf import (
    descriptor as _descriptor,
    message as _message,
    reflection as _reflection,
    symbol_database as _symbol_database
)
import grpc

from .lexer import *
from .grammar import *

logger = logging.getLogger("rpc")


def load_byte(data, lexer=None, parser=None):
    """解析protobuf文件

    Args:
        proto_path (string): protobuf文件路径
        lexer (Lexer): 词法分析
        parser (Parser): 语法分析器
    """
    if not lexer:
        lexer = lex.lex()
    if not parser:
        parser = yacc.yacc(debug=False, write_tables=0)

    lexer.lineno = 1
    result = parser.parse(data)
    result.filename = "haha.proto"
    return result

def load(proto_path, lexer=None, parser=None):
    """解析protobuf文件

    Args:
        proto_path (string): protobuf文件路径
        lexer (Lexer): 词法分析
        parser (Parser): 语法分析器
    """
    proto_path = os.path.abspath(proto_path)

    if not proto_path.endswith('.proto'):
        raise Exception('file name must end with .proto')

    with open(proto_path, 'r') as pf:
        data = pf.read()

    if not lexer:
        lexer = lex.lex()
    if not parser:
        parser = yacc.yacc(debug=False, write_tables=0)

    lexer.lineno = 1
    result = parser.parse(data)
    result.filename = proto_path
    return result


def transform(proto):
    """把load生成的对象转换为原生对象

    Args:
        proto (Protobuf): load返回对象
    """
    file_name = os.path.basename(proto.filename)
    module_name = file_name.replace('.proto', '_pb2')
    proto_module = types.ModuleType(module_name)

    proto_module._sym_db = _symbol_database.Default()
    descriptor = _descriptor.FileDescriptor(
        name=file_name,
        package=proto.package,
        syntax=proto.package,
        serialized_pb=''
    )
    proto_module._sym_db.RegisterFileDescriptor(descriptor)

    # serialized_start和serialized_end真不知道怎么算出来的, 这里就简单的估算一下
    serialized_start = serialized_end = 23 + len(proto.package)
    descriptor_map = {}
    for message_name, message in proto.messages.items():
        fields = []
        for field_name, field in message.fields.items():
            if fields:
                serialized_end += 15
            else:
                serialized_end += 25

            fields.append(_descriptor.FieldDescriptor(
                name=field_name,
                full_name='.'.join((proto.package, message_name, field_name)),
                index=field.index,
                number=field.number,
                type=field.type,
                cpp_type=field.cpp_type,
                label=field.label,
                has_default_value=False,
                default_value=field.default_value,
                message_type=None,
                enum_type=None,
                containing_type=None,
                is_extension=False,
                extension_scope=None,
                options=None,
            ))

        descriptor_map[message_name] = _descriptor.Descriptor(
            name=message_name,
            full_name='.'.join((proto.package, message_name)),
            filename=None,
            file=descriptor,
            containing_type=None,
            fields=fields,
            extensions=[],
            nested_types=[],
            enum_types=[],
            options=None,
            is_extendable=False,
            syntax=proto.syntax,
            extension_ranges=[],
            oneofs=[],
            serialized_start=serialized_start,
            serialized_end=serialized_end,
        )
        serialized_start = serialized_end = serialized_end + 2

    for descriptor_name, des in descriptor_map.items():
        descriptor.message_types_by_name[descriptor_name] = des
        setattr(proto_module, descriptor_name,
                _reflection.GeneratedProtocolMessageType(
                    descriptor_name,
                    (_message.Message,),
                    {
                        'DESCRIPTOR': des,
                        '__module__': module_name
                    }
                ))
        proto_module._sym_db.RegisterMessage(
            getattr(proto_module, descriptor_name))

    return proto_module


def make_client(proto):
    """根据protobuf文件直接生成客户端相关对象"""
    #proto = load(proto_path)
    proto_module = transform(proto)

    for service_name, service in proto.services.items():
        class_name = '{}Stub'.format(service_name)

        def init_method(self, channel):
            for method_name, method in service.methods.items():
                setattr(self, method_name, channel.unary_unary(
                    '/{}/{}'.format('.'.join((proto.package, service_name)),
                                    method_name),
                    request_serializer=getattr(
                        proto_module, method.request_type).SerializeToString,
                    response_deserializer=getattr(
                        proto_module, method.response_type).FromString,
                ))

        stub_class = type(class_name, (object,), {
            '__module__': proto_module.__name__,
            '__init__': init_method
        })
        setattr(proto_module, class_name, stub_class)

    return proto_module

def bind(proto, servicer):
    """根据protobuf文件直接生成服务端相关对象"""

    proto_module = transform(proto)
    rpc_method_handlers = dict()

    for service_name, service in proto.services.items():

        def init_method():
            for method_name, method in service.methods.items():
                from functools import partial
                import inspect

                def simple(fun, return_fun, request, context):
                    args = inspect.getargspec(fun)[0]
                    kwargs = dict()
                    for i in args[1:]:
                        kwargs[i] = getattr(request,i)
                    _result = fun(**kwargs)
                    logger.debug("args:{}".format(kwargs))
                    logger.debug("result:{}".format(_result))
                    return return_fun(_result=_result)
                rpc_method_handlers[method_name] = grpc.unary_unary_rpc_method_handler(
                partial(simple,getattr(servicer, method_name),getattr(proto_module, method.response_type)),
              request_deserializer=getattr(
                        proto_module, method.request_type).FromString,
              response_serializer=getattr(
                        proto_module, method.response_type).SerializeToString,
                )

        init_method()
            # '.'.join((proto.package + str(hex_api.config.HEX_PARTNER_CODE), service_name)),
    generic_handler = grpc.method_handlers_generic_handler(
            '.'.join((proto.package , service_name)),
            rpc_method_handlers)
    return generic_handler

