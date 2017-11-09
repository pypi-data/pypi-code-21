#!/usr/bin/env python
#coding: utf-8

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource




#app = Flask(__name__)
#api = Api(app)

tasks= {}

class ApiServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port

    def get(taskid):
        pass

    def add(taskid, task):
        pass

    def getall(taskid):
        pass

    def serve(self, sts):
        parser = reqparse.RequestParser()
        parser.add_argument('tasktype', type=str)
        parser.add_argument('data', type=str)
        app = Flask(__name__)
        api = Api(app)

        def abort_if_not_exist(taskid):
            abort(404, message="Task {} doesn't exist".format(taskid))

        class AvailableTaskType(Resource):
            def get(self):
                processor_modules = sts.get_processor_modules()
                data = '.'.join(processor_modules.keys())
                return processor_modules

        class TaskApi(Resource):
            def get(self, taskid):
                task = sts.get_task(taskid)
                if task is None:
                    abort(404, message="Task {} doesn't exist".format(taskid))
                return {task.task_id: task.data}

            #def delete(self, taskid):
                #abort_if_not_exist(taskid)
                #del tasks[taskid]
                #return '', 204

            #def put(self, taskid):
                #args = parser.parse_args()
                #task = {'task': args['task']}
                #tasks[taskid] = task
                #return task, 201

        class TaskListApi(Resource):
            def get(self):
                return sts.get_all_task()

            def post(self):
                args = parser.parse_args()
                task = sts.add_task(args.tasktype, args.data)
                resp = {task.task_id: task.type}
                return resp
        
        api.add_resource(AvailableTaskType, '/avail')
        api.add_resource(TaskApi, '/tasks/<taskid>')
        api.add_resource(TaskListApi, '/tasks')
        app.run(host=self.__host, port=self.__port, debug=False)

if __name__ == '__main__':
    server = ApiServer('localhost', 9999)
    server.serve()

        
