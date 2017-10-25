"""
 # Copyright (c) 07 2016 | suryakencana
 # 7/2/16 nanang.ask@kubuskotak.com
 #  __init__.py
"""
from ..ui import helpers as h


def _split_spec(path):
    if ':' in path:
        package, subpath = path.split(':', 1)
        return package, subpath
    else:
        return None, path


def ui_helpers(event):
    context = event.get('context')
    request = event['request']
    settings = request.registry.settings
    egg = settings.get('package')
    assert context, 'No context exists'

    def static_url(path):
        package, subpath = _split_spec(path)
        if package is None:
            path = '{egg}:{static}'.format(static=subpath, egg=egg)
        else:
            path = '{egg}:{static}'.format(static=subpath, egg=package)
        return request.static_url(path)

    event.update({'_context': context, 'egg': egg, 'static': static_url})


def includeme(config):
    config.include('.directive')
    config.add_widgets('ui', h)
    config.add_subscriber(
        '.ui_helpers',
        'pyramid.events.BeforeRender'
    )

