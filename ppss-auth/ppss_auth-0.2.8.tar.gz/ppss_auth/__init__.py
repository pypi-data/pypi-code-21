

from views.admin import Admin,ppssauthpolicy,ACLRoot,getPrincipals
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import SessionAuthenticationPolicy

from models import initdb



configured = False
def includeme(config):
    global configured
    if configured:
        return
    configured = True
    #ppssauthpolicy = PPSSAuthenticationPolicy(config.get_settings())
    settings = config.get_settings()
    Admin.setup(settings)
    config.include("pyramid_beaker")
    config.add_route('ppsslogin', '/login')
    config.add_route('ppsslogout', '/logout')
    config.add_view(Admin,attr='login',route_name="ppsslogin", renderer='ppss_auth:/templates/login.mako')
    config.add_view(Admin,attr='logout',route_name="ppsslogout")


    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(SessionAuthenticationPolicy(callback=getPrincipals) )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(ACLRoot)
    pass
