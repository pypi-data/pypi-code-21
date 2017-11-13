import rx
import jinja2
from dxpy.filesystem import Path


class Service:
    """ Pure logic module
    """
    pass


def template_dir():
    return Path(Path(__file__).father)


def cli_template(name):
    # TODO: Add jinja2 implementation
    with open((template_dir() / 'cli' / 'base.py').abs) as fin:
        tpl = jinja2.Template(fin.read())
    return tpl.render(name=name)


def web_template(name):
    class_names = []
    (rx.Observable.from_(name.split('_'))
     .map(lambda s: s.capitalize())
     .subscribe(class_names.append))
    class_name = ''.join(class_names)
    resource_name = class_name + 'Resource'
    resources_name = class_name + 'sResource'
    imports = """#Auto generated web.py
from flask import Flask, make_response, request, Response
from flask_restful import Resource, reqparse, Api
from . import api
"""

    resource = """
class {name}(Resource):
    def get(self, id):
        try:
            return Response(api.read(id), 200, mimetype="application/json")
        except Exception as e:
            return str(e), 404

    def put(self, id):
        try:
            obj = request.form['obj']
            return Response(api.update(task), 201, mimetype="application/json")
        except Exception as e:
            return str(e), 404

    def delete(self, id):
        try:
            return Response(api.delete(id), 200, mimetype="application/json")
        except Exception as e:
            return str(e), 404
""".format(name=resource_name)

    resources = """
class {name}(Resource):
    import json

    def get(self):
        try:
            objs = []
            api.get_all().subscribe(lambda o: objs.append(o))
            return Response(__class__.json.dumps(objs), 200, mimetype="application/json")
        except Exception as e:
            return str(e), 404

    def post(self):
        obj = request.form['obj']
        result = api.create(obj)
        return Response(__class__.json.dumps({result}), 201, mimetype="application/json")
""".format(name=resources_name, result=r"{'result': result}")

    add_api = """
def add_api(api, root):
    from .config import c
    api.add_resource({name}, c.get_url_endpoint(root))
    api.add_resource({names}, c.get_url_endpoint(root, plural=True))
""".format(name=resource_name, names=resources_name)

    launch_server = """
def launch_server():
    from .config import c
    app = Flask(__name__)
    api = Api(app)
    add_api(api, c.get_root())
    app.run(host=c.ip, port=c.port, debug=c.debug)
"""

    return ''.join([imports, resource, resources, add_api, launch_server])


class SlurmScript:
    def __init__(self, name, path):
        self.path = path
        self.name = name

    def make(self):
        from fs.osfs import OSFS
        with OSFS(self.path) as fs:
            if fs.exists(self.name):
                d = fs.opendir(self.name)
            else:
                d = fs.makedir(self.name)
            with d.open(self.name, 'w') as fout:
                
            d.close()


class Component:
    """ Moduel include api, cli and web interface and an service for logics.
    """

    def __init__(self, name, path):
        self.path = path
        self.name = name

    def _make_init(self, fs):
        fs.touch('__init__.py')

    def _make_api(self, fs):
        with fs.open('api.py', 'w') as fout:
            print('from . import service', file=fout)

    def _make_cli(self, fs):
        with fs.open('cli.py', 'w') as fout:
            print(cli_template(self.name), file=fout)

    def _make_web(self, fs):
        with fs.open('web.py', 'w') as fout:
            print(web_template(self.name), file=fout)

    def _make_service(self, fs):
        with fs.open('service.py', 'w') as fout:
            pass

    def _make_config(self, fs):
        with fs.open('config.py', 'w') as fout:
            pass

    def _make_exceptions(self, fs):
        with fs.open('exceptions.py', 'w') as fout:
            pass

    def _make_tests(self, fs):
        with fs.open('test_{name}.py'.format(name=self.name), 'w') as fout:
            pass

    def make(self):
        from fs.osfs import OSFS
        with OSFS(self.path) as fs:
            if fs.exists(self.name):
                d = fs.opendir(self.name)
            else:
                d = fs.makedir(self.name)
            self._make_init(d)
            self._make_api(d)
            self._make_cli(d)
            self._make_web(d)
            self._make_config(d)
            self._make_service(d)
            self._make_exceptions(d)
            self._make_tests(d)
            d.close()
