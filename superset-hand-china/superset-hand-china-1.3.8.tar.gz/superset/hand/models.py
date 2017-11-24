
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, Boolean,
    DateTime, Date, Table,
    create_engine, MetaData, select
)
from superset.models.helpers import AuditMixinNullable, ImportMixin, set_perm
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
from flask import (
    g, request, redirect, flash, Response, render_template, Markup,
    abort, url_for)

from sqlalchemy.orm import  relationship

class Portal(Model, AuditMixinNullable, ImportMixin):

    """ORM model for portal"""

    __tablename__ = 'portal'
    id = Column(Integer, primary_key=True)
    portal_name = Column(String(250))
    description = Column(Text)
    width = Column(Integer)
    title = Column(String(250))
    logo = Column(String(250))
    footer = Column(String(250))
    portal_href = Column(String(250))
    perm = 'portal|' + portal_name
    menus = relationship("PortalMenu", 
                            back_populates='portal', 
                            cascade="all, delete, delete-orphan")

    export_fields = ('portal_name', 'description', 'title', 'width', 'logo', 'footer', 'portal_href')

    def __repr__(self):
        return self.portal_name

    @renders('portal_name')
    def portal_link(self):
         return Markup('<a target="_blank" href="/hand/portal/{self.id}/show">{self.portal_name}</a>'.format(**locals()))

    @renders('portal_name')
    def portal_link2(self):
        #  return Markup('<a href="/hand/portal/{self.id}/edit">管理</a>'.format(**locals()))
        return Markup('<a href="/hand/portal/{self.id}/edit">'.format(**locals()) + __('manage') + '</a>')
    

    def get_perm(self):
        return (
            "portal|{obj.portal_name}").format(obj=self)
         
role_portal_menu = Table('role_portal_menu', Model.metadata,
    Column('id', Integer, primary_key=True),
    Column('portal_menu_id', Integer, ForeignKey('portal_menu.id')),
    Column('role_id', Integer, ForeignKey('ab_role.id'))
)

class PortalMenu(Model, AuditMixinNullable, ImportMixin):

    """ORM model for portal menu"""

    __tablename__ = 'portal_menu'
    id = Column(Integer, primary_key=True)
    # portal_id = Column(Integer)
    menu_name = Column(String(250))
    parent_id = Column(Integer)
    dashboard_href = Column(String(250))
    open_way = Column(String(32))
    is_index = Column(String(32))
    icon = Column(String(32))
    role_menus = relationship('Role', secondary=role_portal_menu, backref='portal_menus')
    portal_id = Column(Integer, ForeignKey('portal.id'))
    portal = relationship("Portal", 
                        back_populates="menus")

    export_fields = ('menu_name', 'parent_id', 'dashboard_href', 'open_way', 'is_index')


class Mail(Model, AuditMixinNullable, ImportMixin):

    """ORM model for warn mail"""

    __tablename__ = 'warn_mail'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ab_user.id'))
    smtp_server = Column(String(255))
    port = Column(Integer)
    ssl = Column(Boolean)
    email = Column(String(255))
    password = Column(String(255))

class MailLog(Model, AuditMixinNullable, ImportMixin):

    """ORM model form warn mail log"""
    __tablename__ = 'warn_mail_log'
    id = Column(Integer, primary_key=True)
    warn_scheduler_id = Column(Integer, ForeignKey('warn_scheduler.id'))
    subject = Column(String(255))
    sender = Column(String(255))
    receiver = Column(String(255))
    status = Column(Boolean)
    reason = Column(String(255))


class Scheduler(Model, AuditMixinNullable, ImportMixin):

    """ORM model for warn scheduler"""

    __tablename__ = 'warn_scheduler'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ab_user.id'))
    mode = Column(String(255))

    cron_year = Column(String(255))
    cron_month = Column(String(255))
    cron_day = Column(String(255))
    cron_week = Column(String(255))
    cron_day_of_week = Column(String(255))
    cron_hour = Column(String(255))
    cron_minute = Column(String(255))
    cron_second = Column(String(255))
    start_date = Column(String(255))
    end_date = Column(String(255))

    interval_expr = Column(String(255))

    date_run_date = Column(String(255))
    is_active = Column(Boolean)
    is_running = Column(Boolean)


class Condition(Model, AuditMixinNullable, ImportMixin):

    """ORM model for warn condition"""

    __tablename__ = 'warn_condition'
    id = Column(Integer, primary_key=True)
    warn_scheduler_id = Column(Integer, ForeignKey('warn_scheduler.id'))
    scheduler = relationship("Scheduler", backref='condition')
    dashboard_id = Column(Integer, ForeignKey('dashboards.id'))
    slice_id = Column(Integer, ForeignKey('slices.id'))
    metric = Column(String(255))
    expr = Column(String(255))
    receive_address = Column(String(255))
    send_slice_id = Column(Integer, ForeignKey('slices.id'))
    description = Column(String(255))

# portalTheme
class PortalTheme(Model, AuditMixinNullable, ImportMixin):

    """ORM model for portal_theme"""

    __tablename__ = 'portal_theme'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ab_user.id'))
    color = Column(String((255)))
    theme_style = Column(String((255)))
    layout = Column(String((255)))
    header = Column(String((255)))
    top_menu = Column(String((255)))
    sidebar_mode = Column(String((255)))
    sidebar_menu = Column(String((255)))
    sidebar_style = Column(String((255)))
    sidebar_position = Column(String((255)))
    footer = Column(String((255)))

class DownloadQuery(Model, AuditMixinNullable, ImportMixin):
    
    """ORM model for portal_theme"""

    __tablename__ = 'download_query'

    id = Column(Integer, primary_key=True)
    slice_id = Column(Integer)
    sql = Column(Text)
    query_json_url = Column(Text)
    export_json_url = Column(Text)
    columns = Column(Text)
