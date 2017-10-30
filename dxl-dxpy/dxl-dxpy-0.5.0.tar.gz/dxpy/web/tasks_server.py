from flask import Flask, request, jsonify, url_for, make_response
from flask_restful import Resource, Api
import requests

from dxpy.tasks.task import TaskService, TaskSleep


class TaskResource(Resource):
    def get(self, id):
        return str(TaskService.get(id=int(id)))

    def put(self, id):
        task = TaskService.put(**request.form)
        return str(task)


class TasksResource(Resource):
    def get(self):
        return [str(t) for t in TaskService.get_all()]

    def post(self):
        kwargs = {k: request.form[k] for k in request.form}
        task = TaskService.new(**kwargs)
        return str(task), 201

# Server logic


class TaskServer:
    """
    """

    def __init__(self, config_file=None):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_resource(TaskResource, '/api/v0.1/task/<int:id>')
        self.api.add_resource(TasksResource, '/api/v0.1/tasks')

    def start(self, host=None, port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)


server = TaskServer()

if __name__ == "__main__":
    server.start()
