from pyramid.config import Configurator

import pdb


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    #pdb.set_trace()
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_static_view('deform_static', 'deform:static/')
    # add_notfound_view
    config.scan()
    return config.make_wsgi_app()
