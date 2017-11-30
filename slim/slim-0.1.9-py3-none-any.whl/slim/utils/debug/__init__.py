import os
from aiohttp import web
from slim.base.route import Route
from slim.base.view import BaseView

src_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(src_dir, '_debug.html')


class Debug:
    def __init__(self):
        self.view_lst = []

    def add_view(self, view: BaseView, form=None):
        interfaces = []
        for k, v in view._interface.items():
            item = {
                'name': k,
                'route': v
            }
            interfaces.append(item)
        self.view_lst.append(interfaces)

    async def get_data(self, request):
        pass

    async def render(self, request):
        content = open(template_path, encoding='utf8').read().replace('${API_SERVER}', '1233')
        return web.Response(body=content, content_type='text/html')

    def serve(self, route: Route, url):
        def func(app):
            route.get(url + '/data', self.get_data)
            route.get(url, self.render)
        route.before_bind.append(func)
