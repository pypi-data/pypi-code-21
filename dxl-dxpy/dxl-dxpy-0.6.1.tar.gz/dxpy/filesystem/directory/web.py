from flask import request
from flask_restful import Resource
from .model import Directory
from . import service
from ..exceptions import http_error


class DirectoryResource(Resource):
    def get(self, path):
        try:
            return Directory(path, 1).to_serializable(), 200
        except Exception as e:
            return http_error(e)

    def put(self, path):
        try:
            method = request.form.get('method')
            if method == 'cp':
                service.cp(Directory(path), request.form.get('target'))
            elif method == 'mv':
                service.mv(Directory(path), request.form.get('target'))
            return {'status': 'OK'}, 200
        except Exception as e:
            return http_error(e)

    def delete(self, path):
        try:
            service.rm(Directory(path))
            return {'status': 'OK'}, 200
        except Exception as e:
            return http_error(e)


class DirectoriesResource(Resource):
    def post(self):
        try:
            service.mkdir(Directory(request.form.get('path')))
            return {'status': 'OK'}, 201
        except Exception as e:
            return http_error(e)


def add_api(api, root, name='dir'):
    api.add_resource(DirectoryResource, root + '/{0}/<path>'.format(name))
    api.add_resource(DirectoriesResource, root + '/{0}s/<path>'.format(name))
