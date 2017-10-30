from pyramid.response import Response
from pyramid.authentication import AuthTktCookieHelper
from pyramid.settings import asbool
from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,
    Everyone,ALL_PERMISSIONS
    )

from pyramid.view import view_config,forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import logging
l = logging.getLogger('ppssauth')


ppssauthpolicy = None

def getPrincipals(uid,request):
    return request.session.get('principals',[])

class ACLRoot(object):
    __acl__ = [
        (Allow, Authenticated, 'create'),
        (Allow, 'g:editor', 'edit'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]
    def __init__(self, request):
        self.request = request



class Admin():


    @classmethod
    def setup(cls,settings):
        cls.adminname   =settings.get("ppss_auth.adminname","dan")
        cls.adminpass   =settings.get("ppss_auth.adminpass","dan")
        cls.logoutroute = settings.get("ppss_auth.logout_route","home")
        cls.postloginroute = settings.get("ppss_auth.post_login_route","home")
        cls.postloginfollow = settings.get("ppss_auth.post_login_follow","true").lower() == 'true'

    def __init__(self,request):
        self.request = request
        self.user = None

    def login(self):
        l.info("trying login")
        r = self.request
        
        if r.POST:
            username = r.params.get("username",u"")
            password = r.params.get("password",u"")
            l.info("u={username},p={password} ".format(username=username,password=password))
            if username == Admin.adminname and password == Admin.adminpass:
                l.info("{username} logged in".format(username=username) )
                r.session['admin'] = True
                r.session['principals'] = ["g:admin"]
                headers = remember(r, u"1")
                r.userid=u"1"
                return HTTPFound(r.route_url(self.postloginroute),headers=headers)
            return {'msg':'qualcosa &eacute; andato storto'}
        #return Response("ok")
        return{'msg':''}

    def logout(self):
        l.info("logout")
        l.info("principals = {pr}".format(pr=self.request.session.get('principals',[])  ))
        headers = forget(self.request)
        return HTTPFound(self.request.route_url(self.logoutroute),headers=headers)