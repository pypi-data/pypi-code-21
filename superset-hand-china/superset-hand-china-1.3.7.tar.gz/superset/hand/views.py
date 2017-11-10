from superset.views.core import Superset
from superset.views.base import BaseSupersetView
from flask_appbuilder.security.decorators import has_access_api, has_access
from flask_appbuilder import BaseView
# from flask_appbuilder.security.views import UserModelView
from flask_appbuilder.widgets import ListWidget
from flask_appbuilder import expose
from superset.connectors.sqla.models  import TableColumn,SqlMetric
from superset import (
    appbuilder, cache, db, viz, utils, app,
    sm, sql_lab, results_backend, security
)
from flask import (
    g, request, redirect, flash, Response, render_template, Markup,
    abort, url_for, jsonify)
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import asc, and_, desc, select
from flask import request
import sqlalchemy as sa
from past.builtins import basestring
from . import models
import superset.models.core as superset_models
import superset.models.sql_lab as sql_models
from superset.hand.mail import Mail
from superset.hand.scheduler import Scheduler
from superset.hand.models import Portal

from superset.views.base import (
    api, SupersetModelView, BaseSupersetView, DeleteMixin,
    SupersetFilter, get_user_roles, json_error_response, get_error_msg
)
import json
import re
import time
import logging
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
import logging
from flask import request, g
from flask_login import current_user
from flask_appbuilder.security.sqla import models as ab_models
from superset.connectors.sqla.models import Database
from superset.connectors.sqla.models import SqlaTable
import base64

class PortalFilter(SupersetFilter):
    def apply(self, query, func):  # noqa
        if self.has_all_datasource_access():
            return query
        portal_perms = self.get_view_menus('portal_access')
        # query = query.filter(models.Portal.portal_name.in_(portal_perms))
        query = query.filter(models.Portal.perm.in_(portal_perms))
        return query


class PortalModelView(SupersetModelView, DeleteMixin):  # noqa
    datamodel = SQLAInterface(models.Portal)
    list_title = _("List Portal")
    show_title = _("Show Portal")
    add_title = _("Add Portal")
    edit_title = _("Edit Portal")
    list_columns = [
        'portal_link', 'description', 'creator', 'modified', 'portal_link2']
    edit_columns = [
        'portal_name', 'description', 'title',
        'footer', 'portal_href']
    add_columns = edit_columns
    show_columns = add_columns
    base_filters = [['portal_name', PortalFilter, lambda: []]]
    order_columns = ['portal_link', 'description', 'modified']
    page_size = 10
    search_columns = ['portal_name', 'title', 'portal_href', 'changed_on']
    label_columns = {
        'portal_link': _("portal_name"),
        'portal_link2': _("Manage"),
        'portal_name': _("portal_name"),
        'description': _("Description"),
        'creator': _("Creator"),
        'modified': _("Modified"),
        'title': _("title"),
        'footer': _("footer"),
        'portal_href': _("portal_href"),
        'changed_on': _("Changed On"),
    }

    def pre_add(self, obj):
        if not obj.portal_name.strip():
            raise Exception(__("Portal Name can't be empty!"))
        number_of_existing_portals = db.session.query(
            sa.func.count('*')).filter(
            Portal.portal_name == obj.portal_name
        ).scalar()
        # table object is already added to the session
        if number_of_existing_portals > 0:
            raise Exception(
                __("Portal_name [{}] already exists, Please change portal name to add!").format(obj.portal_name))
        security.merge_perm(sm, 'portal_access', obj.get_perm())

    def pre_update(self, obj):
        if not obj.portal_name.strip():
            raise Exception(__("Portal Name can't be empty!"))
        number_of_existing_portals = db.session.query(
            sa.func.count('*')).filter(
            Portal.portal_name == obj.portal_name
        ).scalar()
        # table object is already added to the session
        if number_of_existing_portals > 1:
            raise Exception(
                __("Portal_name [{}] already exists, Please change portal name to save!").format(obj.portal_name))
        # self.pre_add(portal)
        security.merge_perm(sm, 'portal_access', obj.get_perm())

    @expose('/edit/<pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk):
        """Simple hack to redirect to explore view after saving"""
        resp = super(PortalModelView, self).edit(pk)
        if isinstance(resp, basestring):
            return resp
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            abort(404)
        else:
            number_of_existing_portals = db.session.query(
                sa.func.count('*')).filter(
                Portal.portal_name == item.portal_name
            ).scalar()
            if number_of_existing_portals > 1:
                return redirect('portalmodelview/edit/{}'.format(pk))
        return redirect('portalmodelview/list/')


appbuilder.add_view(
    PortalModelView,
    "Portal",
    label=__("Portal"),
    icon="fa-university",
    category="",
    category_icon='',
)




class Hand(BaseSupersetView):

    # 获取所有的切片
    @has_access
    # @csrf.exempt
    @expose("/explore/getSlices", methods=['GET', 'POST'])
    def getSlices(self):
        d = {}
        slices = db.session.query(superset_models.Slice).all()
        for slice in slices:
            d[str(slice.id)] = slice.slice_name
        return json.dumps(d)

    # 获取所有的仪表盘
    @has_access
    @expose("/explore/getDashboards", methods=['GET', 'POST'])
    def getDashboards(self):
        d = {}
        dashboards = db.session.query(superset_models.Dashboard).all()
        for dashboard in dashboards:
            d[str(dashboard.id)] = dashboard.dashboard_title
        return json.dumps(d)

    # 根据sliceId查询slice名称
    @has_access
    @expose("/explore/getSliceName/<slice_id>", methods=['GET', 'POST'])
    def getSliceName(self, slice_id):
        if slice_id != 'undefined':
            slice = db.session.query(
                superset_models.Slice).filter_by(id=slice_id).one()
            return slice.slice_name
        else:
            return 'slice'

    # 根据给定的sliceIds获取slice详情（提示器组合获取子切片及对应数据源）
    @has_access
    @expose("/getSliceData/", methods=['GET', 'POST'])
    def getSliceData(self):
        sliceIds = request.args.get('sliceIds')
        # print(sliceIds)
        slices = []
        datasources = set()
        for slice_id in sliceIds.split(','):
            slice = db.session.query(
                superset_models.Slice).filter_by(id=slice_id).one()
            datasource = slice.datasource
            if datasource:
                datasources.add(datasource)
            # print(slice.data)
            sliceJson = slice.data
            # the filter_box_combination's children
            sliceJson['form_data']['is_child'] = True
            slices.append(sliceJson)
        return json.dumps({"dashboard_data": {"slices": slices},
                           "datasources": {ds.uid: ds.data for ds in datasources},
                           "common": self.common_bootsrap_payload()})

    # 获取提示器组合所有子切片id及名称 添加副
    @has_access
    @expose("/getFilterBoxs/", methods=['GET', 'POST'])
    def getFilterBoxs(self):
        filterBoxs = db.session.query(superset_models.Slice) \
            .filter(superset_models.Slice.viz_type.in_(['filter_box', 'filter_box_tree', 'filter_box_cascade'])) \
            .all()
        filters = []
        for f in filterBoxs:
            slice_name_subtite = None
            if f.subtitle:
                slice_name_subtite = f.slice_name + '[' + f.subtitle + ']'
            else:
                slice_name_subtite = f.slice_name
            filters.append({
                'id': f.id,
                'slice_name': slice_name_subtite
            })
        return json.dumps(filters)

    # 设置提示器缺省值（sql查询设置）
    @has_access
    @expose("/prompt/query", methods=['GET', 'POST'])
    def propmtQuery(self):
        try:
            sql = request.form.get('sql')
            # parse database name from sql
            regex = '[\w_-]+\.[\w_-]+\.[\w_-]+'
            pattern = re.compile(regex)
            l = pattern.findall(sql)
            database_name = l[0].split('.')[0]
            sql = sql.replace(l[0], l[0][(l[0].find('.') + 1):])
            # print(sql)
            session = db.session()
            mydb = session.query(superset_models.Database).filter_by(database_name=database_name).first()
            client_id = str(time.time()).replace('.', '')[2:13]
            query = sql_models.Query(
                database_id=int(mydb.id),
                limit=int(app.config.get('SQL_MAX_ROW', None)),
                sql=sql,
                user_id=int(g.user.get_id()),
                client_id=client_id,
            )
            session.add(query)
            session.commit()
            query_id = query.id

            result = sql_lab.get_sql_results(query_id, return_results=True)
            r = [str(list(d.values())[0]) for d in result['data']]
            return json.dumps(r)
        except Exception as e:
            return utils.error_msg_from_exception(e)

    @expose("/rest/api/sliceUrl", methods=['GET', 'POST'])
    def sliceUrl(self):
        sliceId = request.args.get('sliceId')
        if sliceId:
            slc = db.session.query(
                superset_models.Slice).filter_by(id=sliceId).one()
            return json.dumps({
                'url': slc.slice_url,
                'title': slc.slice_name
            })
        else:
            return False

    @expose("/rest/api/dashboardUrl", methods=['GET', 'POST'])
    def dashboardUrl(self):
        title = request.form['title']
        # groupby = request.form['groupby']
        # group = groupby.split(',')
        slcs = []
        if title:
            dash = db.session.query(
                superset_models.Dashboard).filter_by(id=title).one()
            for slice in dash.slices:
                if slice.viz_type == 'filter_box' or slice.viz_type == 'filter_box_tree':
                    param = json.loads(slice.params)
                    groupby = None
                    if slice.viz_type == 'filter_box':
                        groupby = param['groupby']
                    else:
                        groupby = [param['filter_name'].split('-')[1]]
                    cols = []
                    for col in groupby:
                        cols.append({
                            'extCol': col
                        })
                    slcs.append({
                        'sliceId': slice.id,
                        'columns': cols
                    })
                elif slice.viz_type == 'filter_box_combination':
                    filter_combination = db.session.query(
                        superset_models.Slice).filter_by(id=slice.id).one()
                    filterIds = json.loads(filter_combination.params)[
                        'filter_combination']
                    for filterId in filterIds:
                        filter = db.session.query(
                            superset_models.Slice).filter_by(id=filterId).one()
                        param = json.loads(filter.params)
                        groupby = None
                        if filter.viz_type == 'filter_box':
                            groupby = param['groupby']
                        else:
                            groupby = [param['filter_name'].split('-')[1]]
                        cols = []
                        for col in groupby:
                            cols.append({
                                'extCol': col
                            })
                        slcs.append({
                            'sliceId': filter.id,
                            'columns': cols
                        })
            return json.dumps({
                'url': dash.url,
                'title': dash.dashboard_title,
                'slcs': slcs
            })
        else:
            return False

    @has_access
    @expose("/portal/<portal_id>/<operate>", methods=['GET', 'POST'])
    def portal(self, portal_id, operate):
        portal = db.session.query(models.Portal)\
            .filter_by(id=portal_id).one()
        # query all menu by protal_id
        menus = db.session.query(models.PortalMenu)\
            .filter_by(portal_id=portal_id).all()
        showHeader = 'true'
        d = {
            'portal': (portal.id, portal.portal_name, portal.title, portal.width, portal.logo, portal.footer, portal.portal_href),
            'menus':  [(m.id, m.menu_name, m.parent_id, m.dashboard_href, m.open_way, m.is_index, m.icon) for m in menus],
            'edit': 'false',
            'dashboards': None,
        }
        if operate == 'edit':
            d['edit'] = 'true'
            dashobards = db.session.query(superset_models.Dashboard).all()
            d['dashboards'] = [(d.id, d.dashboard_title) for d in dashobards]
            return self.render_template(
                'hand/portalManage.html',
                bootstrap_data=json.dumps(d, default=utils.json_iso_dttm_ser)
            )
        if operate == 'show':
            # get user info
            # d['roles'] =str(current_user.roles)
            for role in current_user.roles:
                for per in role.permissions:
                    if per.permission.name == 'menu_access':
                        d['showConsole'] = True
                        break
            ms = []
            for role in current_user.roles:
                if str(role) != 'Admin':
                    for m in menus:
                        if m in role.portal_menus:
                            ms.append((m.id, m.menu_name, m.parent_id, m.dashboard_href, m.open_way, m.is_index, m.icon))
                else:
                    ms = [(m.id, m.menu_name, m.parent_id, m.dashboard_href, m.open_way, m.is_index, m.icon) for m in menus]
                    break
            # for role in current_user.roles:
            #     for menu in menus:
            #         m = db.session.execute('select m.id, m.menu_name, m.parent_id, \
            #         m.dashboard_href, m.open_way, m.is_index, m.icon from \
            #         portal_menu m , role_portal_menu rm, '\
            #         'ab_role r  where m.id = rm.portal_menu_id and r.id = rm.role_id and m.id = '\
            #         + str(menu.id) + ' and r.id = ' + str(role.id)).fetchone()
            #         if m != None:
            #             ms.append((m.id, m.menu_name, m.parent_id, m.dashboard_href, m.open_way, m.is_index, m.icon))
            d['menus'] = ms
            d['roles'] = str(current_user.roles)
            d['username'] = current_user.username
            # get portals
            portals = db.session.execute(
                'select id, portal_name from portal').fetchall()
            portalList = []
            for p in portals:
                access = utils.can_access(appbuilder.sm, 'portal_access', 'portal|'+p[1], current_user)\
                or utils.can_access(appbuilder.sm, "all_datasource_access", "all_datasource_access", current_user)
                if access:
                    portalList.append([p[0], p[1]])
            d['portals'] = portalList
            return self.render_template(
                'hand/portalShow.html',
                bootstrap_data=json.dumps(d, default=utils.json_iso_dttm_ser)
            )

    @has_access
    @expose("/menu/<operate>", methods=['GET', 'POST'])
    def addMenu(self, operate):
        data = json.loads(request.form.get('data'))
        try:
            if data['is_index'] == 'true':
                db.session.query(models.PortalMenu) .filter_by(portal_id=str(
                    data['portal_id'])).update({models.PortalMenu.is_index: 'null'})
                # db.session.execute('update portal_menu set is_index = null where portal_id = ' + str(data['portal_id']))
            if operate == 'add':
                addMenu = models.PortalMenu(
                    portal_id=data['portal_id'],
                    menu_name=data['menuName'],
                    parent_id=data['parentSelector'],
                    dashboard_href=data['dashboard_href'],
                    icon=data['picSelector'],
                    is_index=data['is_index'])
                db.session.add(addMenu)
            elif operate == 'modify':
                menu = models.PortalMenu(
                    id=data['id'],
                    portal_id=data['portal_id'],
                    menu_name=data['menuName'],
                    parent_id=data['parentSelector'],
                    dashboard_href=data['dashboard_href'],
                    icon=data['picSelector'],
                    is_index=data['is_index'])
                db.session.query(models.PortalMenu).filter_by(id=menu.id).update(
                    {
                        models.PortalMenu.portal_id: menu.portal_id,
                        models.PortalMenu.menu_name: menu.menu_name,
                        models.PortalMenu.parent_id: menu.parent_id,
                        models.PortalMenu.is_index: menu.is_index,
                        models.PortalMenu.dashboard_href: menu.dashboard_href,
                        models.PortalMenu.icon: menu.icon
                    }
                )
            else:
                menu = models.PortalMenu(id=data['id'])
                db.session.query(models.PortalMenu).filter_by(
                    id=menu.id).delete()
            db.session.commit()
            return 'true'
        except Exception as e:
            logging.exception(e)
            return 'false'

    @has_access
    @expose("/upload/logo", methods=['GET', 'POST'])
    def uploadLogo(self):
        try:
            file = request.files['file']
            filename = 'logo_' + \
                request.form['portal_id'] + '_' + request.form['time'] + '.png'

            # write portal_logo to db
            # db.session.execute("update portal set logo = '%s' where id = %s" %(request.form['time'], request.form['portal_id']))
            db.session.query(models.Portal).filter_by(id=request.form['portal_id']).update(
                {models.Portal.logo: request.form['time']})
            db.session.commit()
            import os
            if not os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir)) + '/assets/resources/portalManage/logo'):
                os.mkdir(os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir)) + '/assets/resources/portalManage/logo')
            file.save(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir)) + '/assets/resources/portalManage/logo/', filename))
            return 'true'
        except Exception as e:
            logging.exception(e)
            return 'false'

    @has_access
    @expose("/logo/del/<id>", methods=['GET', 'POST'])
    def delLogo(self, id):
        try:
            # db.session.execute("update portal set logo = null where id = %s" %(id))
            db.session.query(models.Portal).filter_by(
                id=id).update({models.Portal.logo: "null"})
            db.session.commit()
            return 'true'
        except Exception as e:
            logging.exception(e)
            return 'false'

    @has_access
    @expose("/portal/getTheme", methods=['GET', 'POST'])
    def getPortalTheme(self):
        try:
            # theme = db.session.execute("select * from portal_theme where user_id = " + g.user.get_id()).fetchone()
            theme = db.session.query(models.PortalTheme).filter_by(
                user_id=g.user.get_id()).all()
            if theme == []:
                # init this user theme
                # db.session.execute("insert into portal_theme (user_id, color, theme_style, layout, header, top_menu, sidebar_mode, sidebar_menu, sidebar_style, sidebar_position, footer) values (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
                #                     %(g.user.get_id(), 'blue', 'square', 'fluid', 'fixed', 'light', 'default', 'accordion', 'default', 'left', 'default'))
                addTheme = models.PortalTheme(
                    user_id=g.user.get_id(),
                    color="blue",
                    theme_style="square",
                    layout="fluid",
                    header="fixed",
                    top_menu="light",
                    sidebar_mode='default',
                    sidebar_menu='accordion',
                    sidebar_style='default',
                    sidebar_position='left',
                    footer='default',)

                db.session.add(addTheme)
                db.session.commit()
                # theme = db.session.execute("select * from portal_theme where user_id = " + g.user.get_id()).fetchone()
                theme = db.session.query(models.PortalTheme).filter_by(
                    user_id=g.user.get_id()).all()
            return json.dumps({
                'color': theme[0].color, 'themeStyle': theme[0].theme_style, 'layout': theme[0].layout,
                'header': theme[0].header, 'top_menu': theme[0].top_menu, 'sidebar_mode': theme[0].sidebar_mode,
                'sidebar_menu': theme[0].sidebar_menu, 'sidebar_style': theme[0].sidebar_style, 'sidebar_position': theme[0].sidebar_position, 'footer': theme[0].footer
            })
        except Exception as e:
            logging.exception(e)
            return 'fail'

    @has_access
    @expose("/portal/updateTheme", methods=['GET', 'POST'])
    def updatePortalTheme(self):
        try:
            # db.session.execute("update portal_theme set color = '%s', theme_style = '%s', layout = '%s', header = '%s', top_menu = '%s', sidebar_mode = '%s', sidebar_menu = '%s', sidebar_style = '%s', sidebar_position = '%s', footer = '%s' where user_id = %s"
            #                 %(request.form['color'], request.form['theme_style'], request.form['layout'], request.form['header'], request.form['top_menu'], request.form['sidebar_mode'],
            #                 request.form['sidebar_menu'], request.form['sidebar_style'], request.form['sidebar_position'], request.form['footer'], g.user.get_id()) )
            db.session.query(models.PortalTheme).filter_by(user_id=g.user.get_id()).update({
                models.PortalTheme.color: request.form['color'],
                models.PortalTheme.theme_style: request.form['theme_style'],
                models.PortalTheme.layout: request.form['layout'],
                models.PortalTheme.header: request.form['header'],
                models.PortalTheme.top_menu: request.form['top_menu'],
                models.PortalTheme.sidebar_mode: request.form['sidebar_mode'],
                models.PortalTheme.sidebar_menu: request.form['sidebar_menu'],
                models.PortalTheme.sidebar_style: request.form['sidebar_style'],
                models.PortalTheme.sidebar_position: request.form['sidebar_position'],
                models.PortalTheme.footer: request.form['footer']
            })
            db.session.commit()
            return 'success'
        except Exception as e:
            logging.exception(e)
            return 'fail'

    @has_access
    @expose("/portal/getUserInfo", methods=['GET'])
    def getUserInfo(self):
        user = {
            'username': current_user.username,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'active': current_user.active,
            'roles': str(current_user.roles),
            'login_count': current_user.login_count,
            'email': current_user.email
        }
        return json.dumps(user)

    @has_access
    @expose("/portal/updatePassword", methods=['GET', 'POST'])
    def updatePassword(self):
        try:
            from werkzeug.security import generate_password_hash
            current_user.password = generate_password_hash(
                request.form['newPassword'])
            # print(current_user.__dict__)
            db.session.add(current_user)
            db.session.commit()
            return 'success'
        except Exception as e:
            logging.exception(e)
            return 'fail'

    @has_access
    @expose("/portal/updateUserInfo", methods=['GET', 'POST'])
    def updateUserInfo(self):
        try:
            current_user.first_name = request.form['firstName']
            current_user.last_name = request.form['lastName']
            current_user.email = request.form['email']
            # print(current_user.__dict__)
            db.session.add(current_user)
            db.session.commit()
            return 'success'
        except Exception as e:
            logging.exception(e)
            return 'fail'

    appbuilder.add_link(
        'My Email',
        label=_("My Email"),
        href='/hand/email/show',
        category_icon="fa-flask",
        icon="fa-flask",
        category='Warn',
        category_label=__("Warn"),
    )

    appbuilder.add_link(
        'My Scheduler',
        label=_("My Scheduler"),
        href='/hand/schedulers/list/1',
        icon="fa-search",
        category_icon="fa-flask",
        category='Warn',
        category_label=__("Warn"),
    )

    @has_access
    @expose("/testMail", methods=['GET', 'POST'])
    def testMail(self):
        if request.form['base64'] == 'true':
            password = base64.decodestring(request.form['password'].encode(encoding="utf-8")).decode()
        else:
            password = request.form['password']
        return Mail.testConn(request.form['smtp_server'], request.form['port'], request.form['ssl'],
                            request.form['email'], password)

    @has_access
    @expose("/resetMailPassword", methods=['GET', 'POST'])
    def resetMailPassword(self):
        db.session.query(models.Mail).filter_by(id=request.form['id']).update({
            'password': base64.encodestring(request.form['password'].encode(encoding="utf-8"))
        })
        db.session.commit()
        return 'true'

    @has_access
    @expose("/email/<operate>", methods=['GET', 'POST'])
    def email(self, operate):
        if operate == 'show':
            try:
                mail = db.session.query(models.Mail).filter_by(
                    user_id=g.user.get_id()).one()
                m = mail.__dict__
                del(m['_sa_instance_state'])
            except Exception as e:
                m = None
            d = {
                'mailPage': 'true',
                'mail': m,
                'common': self.common_bootsrap_payload(),
            }
            return self.render_template(
                'hand/scheduler.html',
                bootstrap_data=json.dumps(d, default=utils.json_iso_dttm_ser),
            )
        else:
            data = {}
            try:
                if operate == 'add':
                    add_email = models.Mail(
                        user_id=g.user.get_id(),
                        smtp_server=request.form['smtp_server'],
                        port=request.form['port'],
                        ssl=request.form['ssl'] == 'true' and True or False,
                        email=request.form['email'],
                        password=base64.encodestring(request.form['password'].encode(encoding="utf-8"))
                    )
                    db.session.add(add_email)
                elif operate == 'modify':
                    modify_email = {
                        'smtp_server': request.form['smtp_server'],
                        'port': request.form['port'],
                        'ssl': request.form['ssl'] == 'true' and True or False,
                        'email': request.form['email'],
                    }
                    db.session.query(models.Mail).filter_by(
                        id=request.form['id']).update(modify_email)
                db.session.commit()
                data['status'] = 'true'
            except Exception as e:
                logging.exception(e)
                data['status'] = 'false'
            return json.dumps(data)

    @has_access
    @expose("/schedulers/<operate>/<id>", methods=['GET', 'POST'])
    def getSchedulers(self, operate, id):
        # get all dashboards, slices and metrics
        newDashboards = []
        sendSlices = []
        if operate == 'add' or operate == 'modify':
            for s in db.session.query(superset_models.Slice).all():
                try:
                    try:
                        metrics = json.loads(s.params)['metrics']
                    except Exception as e:
                        metrics = [json.loads(s.params)['metric']]
                    sendSlices.append({
                        'id': s.id,
                        'name': s.slice_name,
                        'metrics': metrics,
                    })
                except Exception as e:
                    # has no metric or metrics
                    pass
            for dashboard in db.session.query(superset_models.Dashboard).all():
                newSlices = []
                for s in dashboard.slices:

                    newSlices.append({
                        'id': s.id,
                        'name': s.slice_name,
                    })

                newDashboards.append({
                    'id': dashboard.id,
                    'name': dashboard.dashboard_title,
                    'slices': newSlices
                })
            # print(sendSlices)
            # print(newDashboards)

        if operate == 'list':
            schedulers = db.session.query(models.Scheduler).filter_by(
                user_id=g.user.get_id()).all()
            ss = []
            for scheduler in schedulers:
                s = scheduler.__dict__
                if len(scheduler.condition) > 0:
                    s['description'] = scheduler.condition[0].description
                    del(s['_sa_instance_state'])
                    del(s['condition'])
                    ss.append(s)
            d = {
                'schedulers': ss,
                'type': 'list',
                'common': self.common_bootsrap_payload(),
            }
        elif operate == 'add':
            d = {
                'type': 'add',
                'dashboards': newDashboards,
                'slices': sendSlices,
                'common': self.common_bootsrap_payload(),
            }
        elif operate == 'modify':
            scheduler = db.session.query(
                models.Scheduler).filter_by(id=id).one()
            condition = scheduler.condition[0]

            s = scheduler.__dict__
            c = condition.__dict__
            del(s['_sa_instance_state'])
            del(s['condition'])
            del(c['_sa_instance_state'])

            d = {
                'type': 'modify',
                'scheduler': s,
                'condition': c,
                'dashboards': newDashboards,
                'slices': sendSlices,
                'common': self.common_bootsrap_payload(),
            }

        return self.render_template(
            'hand/scheduler.html',
            bootstrap_data=json.dumps(d, default=utils.json_iso_dttm_ser),
        )

    @has_access
    @expose("/job/<operate>/<id>", methods=['GET'])
    def operateJob(self, operate, id):
        # scheduler = db.session.query(models.Scheduler).filter_by(id = id).one()
        if operate == 'active':
            try:
                # update is_active and is_running
                modify_scheduler = {
                    'is_active': True,
                    'is_running': True,
                }
                db.session.query(models.Scheduler).filter_by(
                    id=id).update(modify_scheduler)
                Scheduler.add(id)
                db.session.commit()
                return 'true'
            except Exception as e:
                logging.exception(e)
                db.session.rollback()
                return 'false'
        elif operate == 'delete':
            try:
                # delete scheduler
                Scheduler.delete(id)
                # delete mail log
                db.session.query(models.MailLog).filter_by(warn_scheduler_id=id).delete()
                # delete table(scheduler and condition)
                db.session.query(models.Condition).filter_by(warn_scheduler_id=id).delete()
                db.session.query(models.Scheduler).filter_by(id=id).delete()
                db.session.commit()
                return 'true'
            except Exception as e:
                logging.exception(e)
                db.session.rollback()
                return 'false'
        elif operate == 'resume':
            db.session.query(models.Scheduler).filter_by(
                id=id).update({'is_running': True})
            Scheduler.resume(id)
            db.session.commit()
            return 'true'
        elif operate == 'pause':
            db.session.query(models.Scheduler).filter_by(
                id=id).update({'is_running': False})
            Scheduler.pause(id)
            db.session.commit()
            return 'true'

    @has_access
    @expose('/insertOrModifyScheduler/<operate>', methods=['POST'])
    def insertOrModifyScheduler(self, operate):
        data = {}
        try:
            if request.form['mode'] == 'cron':
                # example: month='6-8,11-12', day='3rd fri', hour='0-3'
                cron_year = cron_month = cron_day = cron_week = cron_day_of_week = cron_hour = cron_minute = cron_second = start_date = end_date = None
                cronArray = request.form['expr'].split('&&')
                for cron in cronArray:
                    key = cron.split('=')[0].strip()
                    value = cron.split('=')[1].strip()
                    if value[0] == "'" and value[len(value) - 1] == "'":
                        value = value[1: -1]
                    if key == 'year':
                        cron_year = value
                    elif key == 'month':
                        cron_month = value
                    elif key == 'day':
                        cron_day = value
                    elif key == 'week':
                        cron_week = value
                    elif key == 'day_of_week':
                        cron_day_of_week = value
                    elif key == 'hour':
                        cron_hour = value
                    elif key == 'minute':
                        cron_minute = value
                    elif key == 'second':
                        cron_second = value
                    elif key == 'start_date':
                        start_date = value
                    elif key == 'end_date':
                        end_date = value
                if operate == 'insert':
                    add_scheduler = models.Scheduler(
                        user_id=g.user.get_id(),
                        mode=request.form['mode'],
                        cron_year=cron_year,
                        cron_month=cron_month,
                        cron_day=cron_day,
                        cron_week=cron_week,
                        cron_day_of_week=cron_day_of_week,
                        cron_hour=cron_hour,
                        cron_minute=cron_minute,
                        cron_second=cron_second,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=False,
                        is_running=False,
                    )
                    db.session.add(add_scheduler)
                elif operate == 'modify':
                    modify_scheduler = {
                        'mode': request.form['mode'],
                        'cron_year': cron_year,
                        'cron_month': cron_month,
                        'cron_day': cron_day,
                        'cron_week': cron_week,
                        'cron_day_of_week': cron_day_of_week,
                        'cron_hour': cron_hour,
                        'cron_minute': cron_minute,
                        'cron_second': cron_second,
                        'start_date': start_date,
                        'end_date': end_date,
                    }
                    db.session.query(models.Scheduler).filter_by(
                        id=request.form['id']).update(modify_scheduler)
            elif request.form['mode'] == 'interval':
                # example: hours=2, start_date='2017-3-20'
                interval_expr = start_date = end_date = None
                exprArray = request.form['expr'].split('&&')
                for expr in exprArray:
                    key = expr.split('=')[0].strip()
                    value = expr.split('=')[1].strip()
                    if value[0] == "'" and value[len(value) - 1] == "'":
                        value = value[1: -1]
                    if key == 'start_date':
                        start_date = value
                    elif key == 'end_date':
                        end_date = value
                    else:
                        interval_expr = expr.strip()
                if operate == 'insert':
                    add_scheduler = models.Scheduler(
                        user_id=g.user.get_id(),
                        mode=request.form['mode'],
                        interval_expr=interval_expr,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=False,
                        is_running=False,
                    )
                    db.session.add(add_scheduler)
                elif operate == 'modify':
                    modify_scheduler = {
                        'mode': request.form['mode'],
                        'interval_expr': interval_expr,
                        'start_date': start_date,
                        'end_date': end_date,
                    }
                    db.session.query(models.Scheduler).filter_by(
                        id=request.form['id']).update(modify_scheduler)
            else:
                # example: run_date='2017-3-20 12:00:00'
                date_run_date = request.form['expr'].split('=')[1].strip()[
                    1: -1]
                if operate == 'insert':
                    add_scheduler = models.Scheduler(
                        user_id=g.user.get_id(),
                        mode=request.form['mode'],
                        date_run_date=date_run_date,
                        is_active=False,
                        is_running=False,
                    )
                    db.session.add(add_scheduler)
                elif operate == 'modify':
                    modify_scheduler = {
                        'mode': request.form['mode'],
                        'date_run_date': date_run_date,
                    }
                    db.session.query(models.Scheduler).filter_by(
                        id=request.form['id']).update(modify_scheduler)
            db.session.commit()
            data['status'] = 'true'
            if operate == 'insert':
                scheduler = db.session.query(models.Scheduler).order_by(
                    models.Scheduler.created_on.desc()).first()
                data['schedulerId'] = scheduler.id
        except Exception as e:
            logging.exception(e)
            data['status'] = 'false'
        return json.dumps(data)

    @has_access
    @expose('/insertOrModifyCondition/<operate>', methods=['POST'])
    def insertOrModifyCondition(self, operate):
        data = {}
        try:
            if operate == 'insert':
                add_condition = models.Condition(
                    warn_scheduler_id=request.form['scheduler_id'],
                    dashboard_id=request.form['dashboard_id'],
                    slice_id=request.form['slice_id'],
                    metric=request.form['metric'],
                    expr=request.form['expr'],
                    receive_address=request.form['receive_address'],
                    send_slice_id=request.form['send_slice_id'],
                    description=request.form['description'],
                )
                db.session.add(add_condition)
            elif operate == 'modify':
                modify_condition = {
                    'dashboard_id': request.form['dashboard_id'],
                    'slice_id': request.form['slice_id'],
                    'metric': request.form['metric'],
                    'expr': request.form['expr'],
                    'receive_address': request.form['receive_address'],
                    'send_slice_id': request.form['send_slice_id'],
                    'description': request.form['description'],
                }
                db.session.query(models.Condition).filter_by(
                    id=request.form['id']).update(modify_condition)
            db.session.commit()
            data['status'] = 'true'
        except Exception as e:
            logging.exception(e)
            data['status'] = 'false'
        return json.dumps(data)

    @has_access
    @expose("/getSchedulerLog/<scheduler_id>")
    def getSchedulerLog(self, scheduler_id):
        logs = db.session.query(models.MailLog).filter_by(warn_scheduler_id=scheduler_id) \
                        .order_by(models.MailLog.created_on.desc()).all()
        data = [{
            'subject': log.subject,
            'sender': log.sender,
            'receiver': log.receiver,
            'status': log.status,
            'reason': log.reason,
            'created_on': str(log.created_on)
        } for log in logs]
        return jsonify(data)

    # 查询漏斗图排序类型
    @has_access
    @expose("/queryForFunnel", methods=['GET', 'POST'])
    def queryForFunnel(self):
        print("====queryForFunnel====")
        try:
            # 获取参数
            datasource = request.form.get('datasource')
            groupby = request.form.get('groupby')
            datasource = datasource.split('_')
            # 获取数据ID
            data = datasource[0]
            session = db.session()
            mydb = session.query(SqlaTable).filter_by(id=data).one()
            cols = {col.column_name: col for col in mydb.columns}
            col = cols[groupby].sqla_col
            sql = 'select distinct(temp.%s) from ( %s) temp ' % (col, mydb.sql)
            df = None
            try:
                df = mydb.database.get_df(sql, mydb.schema)
            except Exception as e:
                status = QueryStatus.FAILED
                logging.exception(e)
                error_message = (
                    self.database.db_engine_spec.extract_error_message(e))
            results = []
            for r in df.get(df.columns[0]):
                results.append(r)
            r = {}
            r['results'] = results
            return json.dumps(r)

        except Exception as e:
            return utils.error_msg_from_exception(e)

    def clearMenuAccess(self, role, menu_perm):
        permissions = role.permissions
        # excludeViewIds wont be clear can_list access
        excludeViewIds = []
        for menu in appbuilder.menu.menu:
            if menu.childs:
                for child in menu.childs:
                    if str(child) != "-" and child.baseview != None:
                        view_name = child.baseview.__class__.__name__
                        view = db.session.query(ab_models.ViewMenu).filter_by(name = view_name).one()
                        excludeViewIds.append(view.id)
            else:
                if str(menu) != "-" and menu.baseview != None:
                    view_name = menu.baseview.__class__.__name__
                    view = db.session.query(ab_models.ViewMenu).filter_by(name = view_name).one()
                    excludeViewIds.append(view.id)

        for per in permissions[:]:
            if str(per.permission.name) in tuple(['can_list', 'can_show']) and per.view_menu_id in excludeViewIds:
                permissions.remove(per) 
            if str(per.permission.name) == 'menu_access':
                permissions.remove(per)
        db.session.commit()
            

    def getPerView(self, per, type):
        # get real recoreds in permission_view for each model
        menu_name = None
        try:
            if str(per.permission) == 'datasource_access' and type == 'Tables':
                # view_menu like this: datasource access on datasource|[main].[energy_usage](id:1)
                start = str(per.view_menu).find('.[')
                end = str(per.view_menu).find('](')
                # menu_name like this: energy_usage
                menu_name = str(per.view_menu)[start+2:end]
            if str(per.permission) == 'database_access' and type == 'Databases':
                # view menu like this database access on database|[main].(id:1)
                start =  str(per.view_menu).find('[')
                end = str(per.view_menu).find(']')
                # menu_name like this: main 
                menu_name = str(per.view_menu)[start+1:end]
            if str(per.permission) == 'dashboard_access' and type == 'Dashboard':
                # view_menu like this: dashboard access on dashboard|test
                start = str(per.view_menu).find('|')
                # menu_name like this: test
                menu_name = str(per.view_menu)[start+1:len(str(per.view_menu))]
            if str(per.permission) == 'portal_access' and type == 'Portal List':
                # view_menu like this: portal access on portal|test
                start = str(per.view_menu).find('|')
                # menu_name like this: test
                menu_name = str(per.view_menu)[start+1:len(str(per.view_menu))]
        except Exception as e:
            sep = per.find('|')
            if per.find('|') != -1:
                subView = per[0:sep]
                if subView == 'datasource' and type == 'Tables':
                    # datasource_access
                    start = str(per).find('.[')
                    end = str(per).find('](')
                    menu_name = str(per)[start+2:end]
                if subView == 'database' and type == 'Databases':
                    # database_access
                    start =  str(per).find('[')
                    end = str(per).find(']')
                    menu_name = str(per)[start+1:end]
                if subView == 'dashboard' and type == 'Dashboard':
                    # dashboard_access
                    start = str(per).find('|')
                    # menu_name like this: test
                    menu_name = str(per)[start+1:len(str(per))]
                if subView == 'portal' and type == 'Portal List':
                    # portal_access
                    start = str(per).find('|')
                    # menu_name like this: test
                    menu_name = str(per)[start+1:len(str(per))]
        return menu_name

    def existInArray(self, array, val):
        # return true if val exist in array
        for obj in array:
            if obj == val:
                return True
            return False 
    
    def portalDataAccess(self, node, role):
        showNode = {}
        portals = db.session.query(models.Portal).all()
        views = db.session.query(ab_models.ViewMenu).all()
        portal_nodes = {}
        portal_menu_nodes = {}
        portal_nodes['name'] = __('Portal List')
        portal_nodes['isParent'] = 'true'
        portal_menu_nodes['name'] = __('Show Portal')
        portal_menu_nodes['isParent'] = 'true'
        pns = []
        pmns = []
        for portal in portals:
        # query all menu by protal_id
            menus = db.session.query(models.PortalMenu)\
                        .filter_by(portal_id = portal.id).all()
            children = self.getJsonMenu(0, menus, role)
            portal_menu_node = {
                'name': portal.portal_name,
                'children': children
            }
            portal_node = {
                'name': portal.portal_name,
                'type': 'Portal List'
            }
            for per in role.permissions:
                if str(per.permission) == 'portal_access':
                    menu_name = self.getPerView(per, portal_node['type'])
                    if menu_name == portal.portal_name:
                        portal_node['checked'] = 'true'
            for view in views:
                menu_name = self.getPerView(view.name, portal_node['type'])
                if menu_name == portal.portal_name:
                    portal_node['id'] = view.id 
            pmns.append(portal_menu_node)
            pns.append(portal_node)
        if len(portals) !=0:
            portal_nodes['children'] = pns
            portal_menu_nodes['children'] = pmns
        if node['name'] == __('Portal'):
            node['children'].append(portal_nodes)
            node['children'].append(portal_menu_nodes)
        return node

    def getJsonMenu(self, id, menus, role): 
        if id != 0:
            children = []
            for menu in menus:
                if menu.parent_id == id :
                    node = {
                        'id': menu.id,
                        'name': menu.menu_name,
                        'parent_id': menu.parent_id,
                        'type': 'portal_menu',
                    }
                    for portal_menu in role.portal_menus:
                        if portal_menu.id == menu.id:
                            node['checked'] = 'true'
                    # if len(m) != 0 :
                    #     node['checked'] = 'true'
                    node['children'] = self.getJsonMenu(menu.id, menus, role)
                    children.append(node)
            return children
        nodes = []
        for menu in menus:
            if menu.parent_id == 0:
                node = {
                'id': menu.id,
                'name': menu.menu_name,
                'parent_id': menu.parent_id,
                'type': 'portal_menu',
                }
                # m = db.session.execute('select m.* from portal_menu m , role_portal_menu rm, '\
                #     'ab_role r  where m.id = rm.portal_menu_id and r.id = rm.role_id and m.id = '\
                #     + str(menu.id) + ' and r.id = ' + str(roleId)).fetchall()
                # if len(m) != 0 :
                #     node['checked'] = 'true'
                for portal_menu in role.portal_menus:
                    if portal_menu.id == menu.id:
                        node['checked'] = 'true'
                node['children'] = self.getJsonMenu(menu.id, menus, role)
                nodes.append(node)
        return nodes
    
    @expose("/roles/list", methods=['GET', 'POST'])
    def getRoles(self):
        roles = db.session.query(ab_models.Role).all()
        d = []
        for role in roles:
            d.append({
                "id": role.id,
                "name": role.name,
            })
        return json.dumps(d)

    @expose('/roles/preAdd', methods = ['GET', 'POST'])
    def preAdd(self):
        users = sm.get_all_users()
        data = []
        for user in users:
            data.append({
                "id": user.id,
                "text": user.username
            })
        return self.render_template('hand/role/add.html',users = json.dumps(data))

    @expose('/roles/preEdit/<id>', methods = ['GET', 'POST'])
    def preEdit(self, id):
        role = db.session.query(ab_models.Role).filter_by(id=id).first()
        users = sm.get_all_users()
        data = []
        current_users = []
        for user in users:
            data.append({
                "id": user.id,
                "text": user.username
            })
            for user_role in user.roles:
                if user_role == role:
                    current_users.append(user.id)
        return self.render_template('hand/role/edit.html',users = json.dumps(data)
        ,current_users = json.dumps(current_users), role = role)

    @expose("/roles/shows/<id>", methods=['GET', 'POST'])
    def showRole(self,id):
        data = db.session.query(ab_models.Role).filter_by(id=id).first()
        role = {
            "name": data.name,
            "user": data.user
        }
        return self.render_template('hand/role/show.html',role = role)

    @expose("/roles/adds", methods=['GET', 'POST'])
    def addRole(self):
        roleName = request.form['roleName']
        user_ids = request.form['userIds'].split(',')
        exclude_perm = ['dashboard_access', 'datasource_access', 'schema_access', 
            'database_access', 'portal_access', 'menu_access', 'all_database_access', 'all_datasource_access' ]
         # add role
        role = sm.add_role(roleName)
        perms = db.session.query(ab_models.PermissionView).all()
        perms = [p for p in perms if str(p.permission) not in exclude_perm and p.view_menu]
        for p in perms:
            sm.add_permission_role(role, p)
        #clear perms 
        # for perm in role.permissions[:]:
        #     if str(perm.permission) in ['dashboard_access', 'datasource_access',
        #     'database_access', 'portal_access', 'menu_access', 'all_database_access', 'all_datasource_access' ]:
        #         role.permissions.remove(perm)
        # db.session.commit()
        role.name = roleName
        for user_id in user_ids:
            user = sm.get_user_by_id(user_id)
            if user != None:
                user_roles = user.roles
                user_roles.append(role)
        db.session.commit()
        return redirect('hand/role/role_list.html') 

    @expose("/roles/edits", methods = ["GET", "POST"])
    def editRole(self):
        roleName = request.form['roleName']
        roleId = request.form['roleId']
        userIds = request.form['userIds']
        user_ids = userIds.split(",")
        role = db.session.query(ab_models.Role).filter_by(id = roleId).first()
        users = sm.get_all_users()
        role.name = roleName
        db.session.commit()
        # clear user_roles
        for user in users:
            user_roles = user.roles
            for user_role in user_roles[:]:
                try:
                    user_roles.remove(role)
                except Exception as e:
                    pass
        # add role in user_role
        if userIds:
            for user_id in user_ids:
                user = sm.get_user_by_id(user_id)
                user_roles = user.roles
                exist = self.existInArray(user_roles, role)
                if not exist:
                    user_roles.append(role)
        db.session.commit()
        return redirect('/roles/list')

    @expose("/roles/grant/menu/<id>", methods=['GET', 'POST'])
    def grantMenu(self,id):
        nodes=[]
        menus = appbuilder.menu.menu
        role = db.session.query(ab_models.Role).filter_by(id=id).first()
        views = db.session.query(ab_models.ViewMenu).all()
        for menu in menus:
            node = {}
            children=[]
            for child in menu.childs:
                if str(child) != "-":
                    ch = {}
                    ch['name'] = __(str(child))
                    ch['checked'] = "false"
                    for per in role.permissions:
                        if str(per.permission) == "menu_access" and str(per.view_menu) == str(child):
                            ch['checked'] = "true"
                    for view in views:
                        if view.name == str(child):
                            ch['id'] = view.id
                    children.append(ch)
            node['name'] = __(str(menu.label))  
            node['children'] = children
            node['checked'] = "false"
            for per in role.permissions:
                if str(per.permission) == "menu_access" and str(per.view_menu) == str(menu.label):
                    node['checked'] = "true"
            for view in views:
                if view.name == menu.name:
                    node['id'] = view.id
            nodes.append(node)
        return self.render_template('hand/role/menu_grant.html', node=json.dumps(nodes),
        roleId = id)

    @expose("/roles/grant/menu/save", methods=['GET', 'POST'])
    def saveMenu(self):
        menuIds = request.form['menuIds'].split(',')
        # menuIds = tuple(eval(request.form['menuIds'])) 
        menus = appbuilder.menu.menu
        id = request.form['roleId']
        role = db.session.query(ab_models.Role).filter_by(id=id).first()
        view_menus = db.session.query(ab_models.ViewMenu).filter(ab_models.ViewMenu.id.in_((menuIds))).all()
        menu_perm = tuple(['menu_access', 'can_list', 'can_show'])
        
        # clear menu_access
        self.clearMenuAccess(role, menu_perm)

        # add menu_access
        menu_access_pers = db.session.query(ab_models.Permission)\
        .filter(ab_models.Permission.name.in_((menu_perm))).all()
        for menu_access_per in menu_access_pers:
            for view_menu in view_menus:
                if str(menu_access_per) in ['can_list', 'can_show']:
                    for menu in menus:
                        # add `can_list on RoleModelView`
                        if menu.childs:
                            for child in menu.childs:
                                if str(child) != "-" and child.baseview != None and str(child) == str(view_menu):
                                    view_name = child.baseview.__class__.__name__
                                    perm_view = sm.find_permission_view_menu(menu_access_per.name, view_name)
                                    if perm_view == None:
                                        sm.add_permission_view_menu(menu_access_per.name, view_name)
                                        perm_view = sm.find_permission_view_menu(menu_access_per.name, view_name)
                                    sm.add_permission_role(role, perm_view)
                        else: 
                            if str(menu) != "-" and menu.baseview != None and str(menu) == str(view_menu):
                                view_name = menu.baseview.__class__.__name__
                                perm_view = sm.find_permission_view_menu(menu_access_per.name, view_name)
                                if perm_view == None:
                                    sm.add_permission_view_menu(menu_access_per.name, view_name)
                                    perm_view = sm.find_permission_view_menu(menu_access_per.name, view_name)
                                sm.add_permission_role(role, perm_view)
                else :
                    # add `menu_access on list role`
                    perm_view = sm.find_permission_view_menu(menu_access_per.name, view_menu.name)
                    if perm_view == None:
                        sm.add_permission_view_menu(menu_access_per.name, view_menu.name)
                        perm_view = sm.find_permission_view_menu(menu_access_per.name, view_menu.name)
                    sm.add_permission_role(role, perm_view)
        return redirect('hand/role/role_list.html')

    @expose("/roles/grant/data/<id>", methods=['GET', 'POST'])
    def grantData(self,id):
        menus = appbuilder.menu.menu
        nodes = []
        role = db.session.query(ab_models.Role).filter_by(id=id).first()
        views = db.session.query(ab_models.ViewMenu).all()
        permissions = db.session.query(ab_models.Permission).all()
        for menu in menus:
            node = {}
            children=[]
            if menu.label in ['Sources', 'Portal', 'Dashboards']:
                # sources menu
                if menu.childs:
                    for child in menu.childs:
                        if str(child) != "-" and child.baseview != None and str(child) not in\
                            ['Druid Clusters', 'Druid Datasources']:
                            datas = []
                            ch = {}
                            # get model class like :superset.models.Database
                            obj = child.baseview.datamodel.obj
                            rs = db.session.query(obj).all()
                            for result in rs:    
                                data = {}
                                data['name'] = str(result)
                                data['type'] = str(child)
                                menu_name = None
                                for per in role.permissions:
                                    menu_name = self.getPerView(per, data['type'])
                                    if menu_name == str(result):
                                        data['checked'] = 'true'
                                datas.append(data)
                                for view in views:
                                    menu_name = self.getPerView(view.name, data['type'])
                                    if menu_name == str(result):
                                        data['id'] = view.id
                            ch['name'] = __(str(child))
                            ch['children'] = datas
                            if len(datas) == 0:
                                ch['isParent'] = 'true'          
                            children.append(ch)
                    node['name'] = __(str(menu.label))  
                    node['children'] = children             
                else:
                    #portal and dashboard menu
                    #  dashboard menu
                    datas = []
                    rs = db.session.query(superset_models.Dashboard).all()
                    for result in rs:
                        data = {}
                        data['name'] = str(result)
                        data['type'] = 'Dashboard'
                        menu_name = None
                        perName  = None
                        for per in role.permissions:
                            if str(per.permission) == 'dashboard_access':
                                menu_name = self.getPerView(per, data['type'])
                                if menu_name == str(result):
                                    data['checked'] = 'true'
                        for view in views:
                            menu_name = self.getPerView(view.name, data['type'])
                            if menu_name == str(result):
                                data['id'] = view.id
                        datas.append(data)
                    node['name'] = __(str(menu.label))  
                    node['children'] = datas
                    #  portal menu
                    if menu.label == 'Portal':
                        node['children'] = []
                        self.portalDataAccess(node, role)
                nodes.append(node)
        return self.render_template('hand/role/data_grant.html', node = json.dumps(nodes),
        roleId = id)

    @expose("/roles/grant/data/save", methods=['GET', 'POST'])
    def saveData(self):
        menus = json.loads(request.form['menuIds'])
        id = request.form['roleId']
        role = db.session.query(ab_models.Role).filter_by(id=id).first()
        permissions = role.permissions
                
        # clear data_access
        for per in permissions[:]:
            if str(per.permission) in ['dashboard_access', 'datasource_access', 'database_access', 'portal_access', 'schema_access']:
                permissions.remove(per)
        db.session.commit()   
        # clear portal_menu access
        for portal_menu in role.portal_menus[:]:
            role.portal_menus.remove(portal_menu)
        db.session.commit()   
        # add data_access
        for menu in menus:
            if menu['type'] == 'portal_menu':
                try:
                    portal_menu=db.session.query(models.PortalMenu).filter_by(id = menu['id']).one()
                    role.portal_menus.append(portal_menu)
                    db.session.commit()
                except Exception as e:
                    print(e)
            else:
                view_menu = db.session.query(ab_models.ViewMenu).filter_by(id = menu['id']).first()
                if menu['type'] == 'Tables':
                    permission_name = 'datasource_access'
                if menu['type'] == 'Dashboard':
                    permission_name = 'dashboard_access'
                if menu['type'] == 'Databases':
                    permission_name = 'database_access'
                    # add schema_access for database
                    dbName = self.getPerView(view_menu.name, 'Databases')
                    database = db.session.query(Database).filter_by(database_name = dbName).one()
                    for schema in database.all_schema_names():
                        security.merge_perm(
                            sm, 'schema_access', utils.get_schema_perm(database, schema))
                if menu['type'] == 'Portal List':
                    permission_name = 'portal_access'
                perm_view = sm.find_permission_view_menu(permission_name, view_menu.name)
                if perm_view == None:
                    sm.add_permission_view_menu(permission_name, view_menu.name)
                    perm_view = sm.find_permission_view_menu(permission_name, view_menu.name)
                sm.add_permission_role(role, perm_view)
        return redirect('/roles/list')
   
    @has_access
    @expose('/addQueryHistory', methods=['GET', 'POST'])
    def addQueryHistory(self):
        try:
            add_query = models.DownloadQuery(
                slice_id=request.form['slice_id'],
                query_json_url=request.form['query_json_url'],
                export_json_url=request.form['export_json_url'],
                sql=request.form['sql'],
                columns=request.form['columns'],
            )
            db.session.add(add_query)
            db.session.commit()
            return 'SUCCESS'
        except Exception as e:
            logging.exception(e)
            return 'FAIL'

    @has_access
    @expose("/getDownloadQueryHistory/<slice_id>", methods=['GET', 'POST'])
    def query(self, slice_id):
        def f(obj):
            return {
                'sql': obj.sql,
                'query_json_url': obj.query_json_url,
                'export_json_url': obj.export_json_url,
                'columns': obj.columns,
                'query_time': obj.created_on.strftime("%Y-%m-%d %H:%M:%S")
            }
        querys = db.session.query(models.DownloadQuery).filter_by(
            slice_id=slice_id).order_by(models.DownloadQuery.created_on.desc()).all()
        results = list(map(f, querys))
        return json.dumps(results)

    # @has_access
    @expose("/read/databases", methods=['GET', 'POST'])
    def readDatabases(self):
        ds = []
        databases = db.session.query(Database)\
        .filter_by(expose_in_sqllab = 1)\
        .all()
        for database in databases:
            if self.database_access(database):
                ds.append(database)
        dbs = [
            {'id': str(d.id), 'database_name': repr(d), 'allow_ctas': d.allow_ctas,
            'allow_dml': d.allow_dml, 'allow_run_async': d.allow_run_async,
            'allow_run_sync': d.allow_run_sync, 'expose_in_sqllab': d.expose_in_sqllab,
            'force_ctas_schema': d.force_ctas_schema
            }
            for d in ds 
        ]   
        data = {}
        data['result'] = dbs
        return json.dumps(data)

    @has_access
    @expose("/queryCascadeData", methods=['GET', 'POST'])
    def queryCascadeData(self):
        datasource = request.form.get('datasource')
        groupby = request.form.get('groupby').split(',')
        table = db.session.query(SqlaTable).filter_by(id=datasource.split('__')[0]).one()
        cols = {col.column_name: col for col in table.columns}
        result = {}
        for g in groupby:
            col = cols[g].sqla_col
            sql = 'select distinct(temp.%s) from (%s) temp' % (col, table.sql)
            df = table.database.get_df(sql, table.schema)
            data = df[df.columns[0]].tolist()
            result[g] = data
        return json.dumps(result)

    # 查询所有的模型名称数据
    @has_access
    @expose("/queryTableData", methods=['GET', 'POST'])
    def queryTableData(self):
        def tableMap(obj):
            return {
                'table_name': obj.table_name
            }
        querytables = db.session.query(SqlaTable).all()
        results = list(map(tableMap, querytables))
        return json.dumps(results)

    # 查询所有的切片，副标题名称数据
    @has_access
    @expose("/querySliceData", methods=['GET', 'POST'])
    def querySliceData(self):
        def sliceMap(obj):
            return {
                'slice_name': obj.slice_name,
                'subtitle': obj.subtitle
            }
        queryslices = db.session.query(superset_models.Slice).all()
        results = list(map(sliceMap, queryslices))
        return json.dumps(results)

    # 查询所有的切片，副标题名称数据
    @has_access
    @expose("/queryDashboardData", methods=['GET', 'POST'])
    def queryDashboardData(self):
        def dashboardMap(obj):
            return {
                'dashboard_title': obj.dashboard_title
            }
        querydashboards = db.session.query(superset_models.Dashboard).all()
        results = list(map(dashboardMap, querydashboards))
        return json.dumps(results)

    # 查询仪表盘数据
    @has_access
    @expose("/queryDashboard", methods=['GET', 'POST'])
    def queryDashboard(self):
           
        querydashboards = db.session.query(superset_models.Dashboard).all()
        dashboards =[]
        for i in querydashboards:
            dashboard = {}
            dashboard['id'] = i.id
            dashboard['nick_name'] = i.nick_name
            dashboard['dashboard_title'] = i.dashboard_title
            dashboards.append(dashboard)
        return json.dumps(dashboards)
  

    @has_access
    @expose("/<model>/list")
    def modelview(self, model):
        print(model)
        return render_template("hand/models.html", model=model)

    # 获取columns
    @has_access
    @expose("/<model>/getColumns/<type>")
    def get_columns(self, model, type):
        if model == 'SliceModelView' or model == 'DashboardModelView' or model == 'DatabaseView':
            module = __import__('superset.views.core', fromlist=True)
        elif model == 'TableModelView' or model == 'TableColumnInlineView' or model == 'SqlMetricInlineView':
            module = __import__('superset.connectors.sqla.views', fromlist=True)
        clz = getattr(module, model)
        
        columns = []
        if type == 'edit':
            model_columns = clz.edit_columns
        else:
            model_columns = clz.add_columns
        for column in model_columns:
            try:
                columns.append({
                    'column': column,
                    'type': str(clz.datamodel.list_columns[column].type)
                })
            except Exception as e:
                columns.append({
                    'column': column,
                    'type': 'CASCADE'
                })
        return json.dumps(columns)

    # 获取所有的数据库连接
    @has_access
    @expose("/explore/getDatabases", methods=['GET', 'POST'])
    def getDatabases(self):
        d = {}
        databases = db.session.query(superset_models.Database).all()
        for database in databases:
            d[str(database.id)] = database.verbose_name if database.verbose_name else database.database_name
        return json.dumps(d)

    # 获取所有tables
    @has_access
    @expose("/explore/getTables", methods=['GET', 'POST'])
    def getTables(self):
        d = {}
        tables = db.session.query(SqlaTable).all()
        for table in tables:
            d[str(table.id)] =  table.table_name
        return json.dumps(d)

    # 更新dashboard_slices table
    @has_access
    @expose("/updateDashboardSlices", methods=['GET', 'POST'])
    def updateDashboardSlices(self):
        if request.form['type'] == 'dashboard':
            # delete
            dashboard_id = request.form['dashboard_id']
            print(dashboard_id)
            db.session.execute('delete from dashboard_slices where dashboard_id = %s' %(dashboard_id))
            db.session.commit()
            # add
            for sliceId in request.form['slices'].split(','):
                db.session.execute('insert into dashboard_slices (dashboard_id, slice_id) values (%s, %s)' %(dashboard_id, sliceId))
            db.session.commit()
        else:
            slice_id = request.form['slice_id']
            db.session.execute('delete from dashboard_slices where slice_id = %s' %(slice_id))
            db.session.commit()
            # add
            for dashboardId in request.form['dashboards'].split(','):
                db.session.execute('insert into dashboard_slices (dashboard_id, slice_id) values (%s, %s)' %(dashboardId, slice_id))
            db.session.commit()
        return 'SUCCESS'

appbuilder.add_view_no_menu(Hand)
