from __future__ import (absolute_import, division, print_function)

import urllib

import werkzeug
from flask import Flask, render_template, current_app, make_response, request
from wof.flask.config import Config
import datetime

import wof
from wof.core import wofConfig, getSpyneApplications
import wof.core_1_1 as wof_1_1
import wof.core_1_0 as wof_1_0

try:
    from wof import __version__, core_1_0, core_1_1

    version = __version__
except ImportError:
    version = 'dev'

def create_simple_app():
    app = Flask(__name__)

    app.config.from_object(config.Config)
    return app

#TODO: Error handlers (404, etc.)
def create_app(wof_inst, wof_inst_1_1, soap_service_url=None, soap_service_1_1_url=None):
    # app = Flask(__name__)
    #
    # app.config.from_object(config.Config)
    app = create_simple_app()
    path = wof_inst.urlpath.lower()
    servicesPath =  '/'+wof_inst.urlpath.lower()
    add_flask_routes(app,path,servicesPath,wof_inst,
                     wof_inst_1_1,soap_service_url=soap_service_url, soap_service_1_1_url=soap_service_1_1_url )
    return app

def add_flask_routes(app,path, servicesPath,
                     wof_inst,
                     wof_inst_1_1,
                     soap_service_url=None,
                     soap_service_1_1_url=None):

    # app.wof_inst = wof_inst
    # app.wof_inst_1_1 = wof_inst_1_1
    # path = wof_inst.network
    # servicesPath =  '/'+wof_inst.network

    #@app.route( '/')
    def index():
        return render_template('index.html',
                               rest10=path+'/rest_1_0/',
                               rest11=path+'/rest_1_1/',
                               rest2=path+'/rest_2/',
                               soap10=path+'/soap/cuahsi_1_0/',
                               soap11=path+'/soap/cuahsi_1_1/',
                               p=wof_inst.network,
                               urlpath=wof_inst.urlpath,
                               ver=version,
                               organization=wof_inst_1_1.organization,
                               address=wof_inst_1_1.address,
                               city=wof_inst_1_1.city,
                               state=wof_inst_1_1.state,
                               zipcode=wof_inst_1_1.zipcode,
                               contactname=wof_inst_1_1.contactname,
                               contactemail=wof_inst_1_1.contactemail,
                               phone=wof_inst_1_1.phone,
                               link=wof_inst_1_1.link)

    app.add_url_rule(servicesPath+'/', wof_inst.urlpath+'index', index)

    def index_2_0():
        return render_template('index_2.html',
                       path= path + '/rest/2/',
                       p=wof_inst.network,
                       urlpath=wof_inst.urlpath,
                       s=wof_inst.default_site,
                       v=wof_inst.default_variable,
                       sd=wof_inst.default_start_date,
                       ed=wof_inst.default_end_date,
                       u=wof_inst.default_unitid,
                       sm=wof_inst.default_samplemedium,
                       ver=version,
                       organization=wof_inst.organization,
                       address=wof_inst.address,
                       city=wof_inst.city,
                       state=wof_inst.state,
                       zipcode=wof_inst.zipcode,
                       contactname=wof_inst.contactname,
                       contactemail=wof_inst.contactemail,
                       phone=wof_inst.phone,
                       link=wof_inst.link)
    app.add_url_rule(servicesPath+'/rest_2/', wof_inst.urlpath+'index_2_0', index_2_0)

    if wof_inst is not None:
        if not 'SOAP_SERVICE_URL' in app.config and soap_service_url:
            app.config['SOAP_SERVICE_URL'] = soap_service_url

        #@app.route('/rest_1_0/')
        def index_1_0():
            return render_template('index_1_0.html',
                           path= path + '/rest/1_0/',
                           p=wof_inst.network,
                           urlpath=wof_inst.urlpath,
                           s=wof_inst.default_site,
                           v=wof_inst.default_variable,
                           sd=wof_inst.default_start_date,
                           ed=wof_inst.default_end_date,
                           u=wof_inst.default_unitid,
                           sm=wof_inst.default_samplemedium,
                           ver=version,
                           organization=wof_inst.organization,
                           address=wof_inst.address,
                           city=wof_inst.city,
                           state=wof_inst.state,
                           zipcode=wof_inst.zipcode,
                           contactname=wof_inst.contactname,
                           contactemail=wof_inst.contactemail,
                           phone=wof_inst.phone,
                           link=wof_inst.link)
        app.add_url_rule(servicesPath+'/rest_1_0/',wof_inst.urlpath+ 'index_1_0', index_1_0)



        # #@app.route('/soap/wateroneflow.wsdl')
        # def get_wsdl():
        # #TODO: The WSDL should be served separately from the Flask application.
        # # Come up with a better way to do this.
        #     network = wof_inst.network.lower()
        #
        #     try:
        #         serv_loc = app.config['SOAP_SERVICE_URL']
        #     except KeyError:
        #         serv_loc = app.config.get(
        #             'SOAP_SERVICE_URL',
        #             '%s/wateroneflow/' % request.url.rsplit('/', 1)[0])
        #
        #     response = make_response(render_template('wsdl_temp.wsdl',
        #                                      serv_loc=serv_loc,
        #                                      network=network))
        #
        #     response.headers['Content-Type'] = 'text/xml'
        #     return response
        # app.add_url_rule(servicesPath+'/soap/wateroneflow.wsdl', wof_inst.network+'get_wsdl', get_wsdl)

    if wof_inst_1_1 is not None:
        if not 'SOAP_SERVICE_URL_1_1' in app.config and soap_service_1_1_url:
            app.config['SOAP_SERVICE_URL_1_1'] = soap_service_1_1_url

        #@app.route('/rest_1_1/')
        def index_1_1():
            return render_template('index_1_1.html',
                           path=path+'/rest/1_1/',
                           urlpath=wof_inst.urlpath,
                           p=wof_inst_1_1.network,
                           s=wof_inst_1_1.default_site,
                           v=wof_inst_1_1.default_variable,
                           sd=wof_inst_1_1.default_start_date,
                           ed=wof_inst_1_1.default_end_date,
                           w=wof_inst_1_1.default_west,
                           so=wof_inst_1_1.default_south,
                           n=wof_inst_1_1.default_north,
                           e=wof_inst_1_1.default_east,
                           ver=version,
                           organization=wof_inst_1_1.organization,
                           address=wof_inst_1_1.address,
                           city=wof_inst_1_1.city,
                           state=wof_inst_1_1.state,
                           zipcode=wof_inst_1_1.zipcode,
                           contactname=wof_inst_1_1.contactname,
                           contactemail=wof_inst_1_1.contactemail,
                           phone=wof_inst_1_1.phone,
                           link=wof_inst_1_1.link)
        app.add_url_rule(servicesPath+'/rest_1_1/', wof_inst.urlpath+'index_1_1', index_1_1)

        #@app.route('/soap/wateroneflow_1_1.wsdl')
        # def get_wsdl_1_1():
        # #TODO: The WSDL should be served separately from the Flask application.
        # # Come up with a better way to do this.
        #     network = wof_inst_1_1.network.lower()
        #
        #     try:
        #         serv_loc = app.config['SOAP_SERVICE_URL_1_1']
        #     except KeyError:
        #         serv_loc = app.config.get(
        #             'SOAP_SERVICE_URL_1_1',
        #             '%s/wateroneflow_1_1/' % request.url.rsplit('/', 1)[0])
        #
        #     response = make_response(render_template('wsdl_1_1_template.wsdl',
        #                                      serv_loc=serv_loc,
        #                                      network=network))
        #
        #     response.headers['Content-Type'] = 'text/xml'
        #     return response
        # app.add_url_rule(servicesPath+'/soap/wateroneflow_1_1.wsdl', wof_inst.network+'get_wsdl_1_1', get_wsdl_1_1)


    return app


def site_map_flask_wsgi_mount(app):
    output = []
    for mount in app.wsgi_app.mounts:
        method = app.wsgi_app.mounts[mount].app.name
        #methods = ','.join(mounts[.app.name)
        #path = mount.key
        #line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        line = urllib.unquote("{}".format(mount))
        if '/static/' in line:
            #or '/rest/' in line:
            continue
        output.append(line)

    #print "Acess Service Path at "
    #for line in sorted(output):
    #    print(line)
    return sorted(output)


def create_wof_flask_app(dao, config_file):
    """
    Returns a fully instantiated WOF wsgi app (flask + apps)
    """

    # wof_obj_1_0 = wof_1_0.WOF(dao, config_file)
    # wof_obj_1_1 = wof_1_1.WOF_1_1(dao,config_file)
    #
    # # static URL's need to be deprecriated.
    # app = wof.flask.create_app(wof_obj_1_0,wof_obj_1_1)
    #
    # spyneapps = getSpyneApplications(wof_obj_1_0,wof_obj_1_1)
    # app.wsgi_app = werkzeug.wsgi.DispatcherMiddleware(app.wsgi_app, spyneapps)
    wConf = wofConfig(dao=dao, wofConfigFile=config_file)
    templates = None
    if hasattr(wConf, 'configObject' ):
        if hasattr(wConf.configObject, 'TEMPLATES' ):
            templates = wConf.configObject.TEMPLATES

    app = create_wof_flask_multiple({wConf},templates=templates)
    return app


def create_wof_flask_multiple(wofConfig=[], templates=None):
    """
    Returns a fully instantiated WOF wsgi app (flask + apps)
    """
    app = wof.flask.create_simple_app()
    spyneapps = {}
    for wConf in wofConfig:
        wof_obj_1_0 = wof_1_0.WOF(wConf.dao, wConf.config, templates)
        wof_obj_1_1 = wof_1_1.WOF_1_1(wConf.dao,wConf.config,templates)

        spyneapps.update(getSpyneApplications(wof_obj_1_0,wof_obj_1_1,templates) )
        path = wof_obj_1_0.urlpath.lower()
        servicesPath =  '/'+wof_obj_1_0.urlpath.lower()
        wof.flask.add_flask_routes(app,path, servicesPath,
                     wof_obj_1_0,
                     wof_obj_1_1,
                     soap_service_url=None,
                     soap_service_1_1_url=None)

    app.wsgi_app = werkzeug.wsgi.DispatcherMiddleware(app.wsgi_app, spyneapps)
    return app
