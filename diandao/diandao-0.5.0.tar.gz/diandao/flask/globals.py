# -*- coding: utf-8 -*-

from functools import partial
from werkzeug.local import LocalStack, LocalProxy
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_rq import RQ
from celery import Celery
from flask_sqlalchemy import _BoundDeclarativeMeta, declarative_base, _QueryProperty, Model as BaseModel

redis = FlaskRedis()
db = SQLAlchemy(session_options={"autoflush":False})
celery = Celery()
rq = RQ()


class ModelMeta(_BoundDeclarativeMeta):
    def __new__(cls, name, bases, d):
        return _BoundDeclarativeMeta.__new__(cls, name, bases, d)

    def __init__(cls, name, bases, d):
        _BoundDeclarativeMeta.__init__(cls, name,bases, d)
        # 检测Sqllog字段, 绑定日志配置
        for k, v in d.items():
            if isinstance(v, object) and getattr(v, "__sql_log__", None):
                setattr(cls, k, v.bind_model(cls))
                break
        # auto_cache特性
        # 暂无法找到方法实现自动

# The following copied from how flask_sqlalchemy creates it's Model
Model = declarative_base(cls=BaseModel, name='Model', metaclass=ModelMeta)
Model.query = _QueryProperty(db)


# Need to replace the original Model in flask_sqlalchemy, otherwise it
# uses the old one, while you use the new one, and tables aren't
# shared between them
db.Model = Model


stacker = {
    "app": None
}

def _lookup_(name):
    return stacker[name]

app=LocalProxy(partial(_lookup_,"app"))