import requests
import json
from functools import wraps
from flask import Flask, make_response, request, Response
from flask_restful import Resource, reqparse, Api

from ..model import task
from .. import interface
from .. import provider


class TaskResource(Resource):
    def get(self, id):
        try:
            return Response(interface.read(id).to_json(), 200, mimetype="application/json")
        except TaskNotFoundError as e:
            return str(e), 404

    def put(self, id):
        try:
            t = task.Task.from_json(request.form['task'])
            return Response(interface.update(t), 201, mimetype="application/json")
        except TaskNotFoundError as e:
            return str(e), 404

    def delete(self, id):
        try:
            return Response(interface.delete(id), 200, mimetype="application/json")
        except TaskNotFoundError as e:
            return str(e), 404


class TasksResource(Resource):
    def get(self):
        tasks = []
        interface.read_all().subscribe(lambda t: tasks.append(t))
        ts = '[\n' + ',\n'.join([t.to_json() for t in tasks]) + '\n]'
        return Response(ts, 200, mimetype="application/json")

    def post(self):
        t = task.Task.from_json(request.form['task'])
        res = interface.create(t)
        return Response(json.dumps({'id': res}), 201, mimetype="application/json")


def add_apis(api, root, name='task'):
    root_tsk = root + '/{0}'.format(name)
    api.add_resource(TaskResource, root_tsk + '/<int:id>')
    api.add_resource(TasksResource, root_tsk + 's')


def add_api(api):
    c = provider.get_or_create_service('config').get_config('interface')
    api.add_resource(TaskResource, c.task_url + '/<int:id>')
    api.add_resource(TasksResource, c.tasks_url)


def lauch_database_server():
    app = Flask(__name__)
    api = Api(app)
    add_api(api)
    c = provider.get_or_create_service('config').get_config('interface')
    app.run(host=c.ip, port=c.port, debug=c.debug)
