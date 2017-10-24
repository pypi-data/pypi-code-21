# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask import request, g

from extensions import db, admin
import models
import views.admin

from .. import constants


def create_app(config, name=None):
    if not name:
        name = __name__

    app = Flask(name)

    app.config.from_mapping(constants.CONFIG)

    # 相对当前工作目录
    config = os.path.join(os.getcwd(), config)
    app.config.from_pyfile(config)

    configure_logging(app)
    configure_extensions(app)
    configure_context_processors(app)
    configure_handlers(app)
    configure_views(app)

    return app


def configure_logging(app):
    import logging.config

    if 'LOGGING' in app.config:
        # 有可能没配置
        app.logger and logging.config.dictConfig(app.config['LOGGING'])


def configure_extensions(app):
    """
    初始化插件
    """
    db.init_app(app)

    admin.init_app(app)


def configure_context_processors(app):
    """
    模板变量
    """
    pass


def configure_handlers(app):
    """
    before_request之类的处理
    """

    @app.before_request
    def init_libs():
        """
        初始化各种库
        """
        from .backends.ding import DingBackend
        from .backends.sendcloud import SendCloudBackend
        from .backends.mail import MailBackend

        g.ding = DingBackend(
            app.config['DING_CORP_ID'],
            app.config['DING_CORP_SECRET'],
            app.config['DING_AGENT_ID'],
        )

        if 'SEND_CLOUD_API_USER' in app.config:
            g.send_cloud = SendCloudBackend(
                app.config['SEND_CLOUD_API_USER'],
                app.config['SEND_CLOUD_API_KEY'],
                app.config['SEND_CLOUD_SENDER'],
            )
        else:
            g.send_cloud = None

        if 'MAIL_SENDER_LIST' in app.config:
            g.mail = MailBackend(app.config['MAIL_SENDER_LIST'])
        else:
            g.mail = None


def configure_views(app):
    """
    注册views
    """
    import views.frontend

    # 注册 admin views
    views.admin.register_views(app)

    app.register_blueprint(views.frontend.bp)
