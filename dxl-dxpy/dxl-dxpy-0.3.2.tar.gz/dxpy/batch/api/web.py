# Auto generated web.py
from flask import Flask, make_response, request, Response
from flask_restful import Resource, reqparse, Api
from . import api

# TODO: Implementation
raise NotImplementedError


class BatchResource(Resource):
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


class BatchsResource(Resource):
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
        return Response(__class__.json.dumps({'result': result}), 201, mimetype="application/json")


def add_api(api, root):
    from .config import c
    api.add_resource(BatchResource, c.get_url_endpoint(root))
    api.add_resource(BatchsResource, c.get_url_endpoint(root, plural=True))


def launch_server():
    from .config import c
    app = Flask(__name__)
    api = Api(app)
    add_api(api, c.get_root())
    app.run(host=c.ip, port=c.port, debug=c.debug)
