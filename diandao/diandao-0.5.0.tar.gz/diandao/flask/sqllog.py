# -*- coding: utf-8 -*-
from diandao.flask.cacheable import CacheableBase
from diandao.flask.application import db
from sqlalchemy import Column, Integer, String, BIGINT, TIMESTAMP, DATE, Enum, Boolean, event, or_, not_, Text, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.attributes import InstrumentedAttribute, get_history
from datetime import datetime
from diandao.flask import operator_id as operator_id_handle, operator_role as operator_role_handle, \
    operator_name as operator_name_handle, app
from diandao.sqlalchemy.types import JSONSerializer
from diandao import JSON
from functools import wraps
from diandao import compact, extract
from flask import render_template_string
from sqlalchemy import event, inspect
from flask_rq import job
import re
from numbers import Number


class SqllogBase(db.Model):
    """基本日志模型
    """
    __sql_log__ = "0.1.0"
    __abstract__ = True
    __bind_model__ = None
    __bind_key__ = app.config.get("SQLLOG_BIND_KEY", None)
    __tablename__ = app.config.get("SQLLOG_TABLENAME", "sqllog")
    __session__ = db.session
    # 监听的SQL事件
    listen = ("insert", "update", "delete")
    # 不记录属性变化数据(建议忽略大数据的字段)
    truncated_fields = tuple()

    __message_default_templates__ = dict(
        insert="{operator}创建了{model}#{target_id}",
        update="{operator}更新了{model}#{target_id}：{fields sp=，}{key}=>{after}{/fields}",
        delete="{operator}删除了{model}#{target_id}"
    )
    # 简易消息模板配置, 未设置会使用默认配置 __message_default_templates__
    # 模板变量:
    #   operator:       优先显示操作者的名字或 {role}#{id}
    #   operator_id:    操作者ID(未设置为0)
    #   operator_role:  操作者角色(如有,如Admin, 默认为空)
    #   operator_name:  操作者名称, 默认为"unset"
    #   model:  监听的模型类名
    #   target_id: 模型实例ID
    #
    #   仅update时:
    #   {fields sp=分割符}遍历变更字段{/fields}
    #   key: 字段名
    #   before: 变更前值(json)
    #   after: 变更后值(json)
    #
    message_templates = dict()

    # Table fields
    id = Column(BIGINT, primary_key=True)
    message = Column(Text, doc="简易消息文本日志")
    action = Column(Enum("insert", "update", "delete"), default="update", server_default="update", doc="日志类型")
    model = Column(String(32), index=True, default="", server_default="", doc="模型名称")
    target_id = Column(BIGINT, default="0", server_default="0", doc="模型实例的ID")
    operator_id = Column(BIGINT, default=operator_id_handle, server_default="0", doc="操作人id")
    operator_role = Column(String(32), default=operator_role_handle, server_default="", doc="操作人角色")
    operator_name = Column(String(32), default="", server_default="", doc="操作人名")
    # json数据, 保存发生变化的属性数据
    # {
    #   "key1":[before, after],
    #   "key2":[before, after]
    # }
    changes = Column(JSONSerializer, doc="字段变更详情")
    # 创建时间
    ctime = Column(TIMESTAMP, default=datetime.now, doc='创建时间, 默认为当前时间')

    def __init__(self, action, target):
        cls = self.__class__
        model_cls = target.__class__
        pk = get_pk(model_cls)
        self.action = action
        self.model = model_cls.__name__
        self.target_id = getattr(target, pk, 0)
        operator = cls.operator_handle(target, action)
        self.operator_id = operator[0]
        self.operator_role = operator[1]
        self.operator_name = operator[2]
        self.changes = cls.__get_changes(target)
        self.message = cls.__render_message(self)

    @classmethod
    def __render_message(cls, log):
        operator_id = log.operator_id
        operator_role = log.operator_role
        operator_name = log.operator_name
        action = log.action
        model = log.model
        target_id = log.target_id
        operator = operator_name
        changes = log.changes
        if operator_name == "System" and (operator_role or operator_id):
            operator = "%s#%s" % (operator_role, operator_id)
        # 模块配置
        templates = cls.__message_default_templates__.copy()
        templates.update(cls.message_templates)
        template = templates.get(action, "模板获取错误")
        if callable(template):
            template = template(log)
        contexts = compact("operator_id", "operator_role", "operator_name", "operator", "action", "model", "target_id")
        # update fields
        if action == "update":
            field_re = re.compile('\{fields sp=(.*?)\}(.*)\{/fields\}', flags=re.DOTALL | re.I | re.U)
            field_finds = field_re.findall(template)
            if field_finds:
                template = field_re.sub("{fields}", template)
                sp = field_finds[0][0]
                tpl = field_finds[0][1]
                chstr = []
                for k, v in log.changes.items():
                    kstr = tpl.replace("{key}", k).replace("{before}", JSON.stringify(v[0])).\
                        replace("{after}", JSON.stringify(v[1]))
                    chstr.append(kstr.encode("utf-8"))
                contexts.setdefault("fields", sp.join(chstr))

        for k, v in contexts.items():
            replace = re.compile('\{%s\}' % k, flags=re.U)
            if isinstance(v, unicode):
                v = v.encode("utf-8")
            template = replace.sub("%s" % v, template)
        return template

    @classmethod
    def __get_changes(cls, target):
        changes = dict()
        model = target.__class__
        for k, v in model.__dict__.items():
            if isinstance(v, InstrumentedAttribute):
                his = get_history(target, k)
                if his.deleted:  # 有删除的数据
                    if k in cls.truncated_fields:
                        changes.setdefault(k, ["[truncated]", "[truncated]"])
                    else:
                        if his.deleted[0] == his.added[0]:
                            continue
                        if isinstance(his.deleted[0], Number) and his.deleted[0] == float(his.added[0]):
                            continue
                        changes.setdefault(k, [his.deleted[0], his.added[0]])
                continue
        return changes

    @classmethod
    def operator_handle(cls, target, action, **kwargs):
        return (operator_id_handle(), operator_role_handle(), operator_name_handle() or "System")

    @classmethod
    def bind_model(cls, model):
        if cls.__bind_model__:
            if cls.__bind_model__ != model:
                raise Exception("每个SqllogBase类只能绑定一个模型类!")
            return  # 已经绑定过了
        cls.__bind_model__ = model
        listen_log(cls)


def listen_log(loger):
    """
    监听模型数据变动
    :param loger:
    :param listen:
    :param fields:
    :return:
    """
    # 获取绑定的数据模型
    model = loger.__bind_model__

    @event.listens_for(model, 'after_update')
    def after_update_handel(mapper, connection, target):
        if "update" in loger.listen:
            make_log(loger, "update", target)

    @event.listens_for(model, 'after_insert')
    def after_insert_handel(mapper, connection, target):
        if "insert" in loger.listen:
            make_log(loger, "insert", target)

    @event.listens_for(model, 'after_delete')
    def after_delete_handel(mapper, connection, target):
        if "delete" in loger.listen:
            make_log(loger, "delete", target)


def get_pk(cls):
    if getattr(cls, "__pk__", None):
        return cls.__pk__
    detection = inspect(cls)
    pks = detection.primary_key
    pk = pks[0].name if len(pks) else None
    cls.__pk__ = pk
    return pk


def make_log(loger, action, target):
    log = loger(action=action, target=target)
    add_log.delay(log)


@job("default")
def add_log(log):
    db.session.add(log)
    db.session.commit()