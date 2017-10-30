from flask import request
from flask_restful import Resource
from .model import File
from . import service
from ..exceptions import http_error


class FileResource(Resource):
    def get(self, path):
        try:
            is_load = request.args.get('is_load')
            if is_load is None or is_load is False:
                load_depth = 0
            else:
                load_depth = 1
            return File(path, load_depth).to_serializable(), 200
        except Exception as e:
            return http_error(e)

    def put(self, path):
        try:
            method = request.form.get('method')
            if method == 'cp':
                service.cp(File(path), request.form.get('target'))
            elif method == 'mv':
                service.mv(File(path), request.form.get('target'))
            elif method == 'modify':
                File(path).save(request.form.get('data'))
            return {'status': 'OK'}, 200
        except Exception as e:
            return http_error(e)

    def delete(self, path):
        try:
            service.rm(File(path))
            return {'status': 'OK'}, 200
        except Exception as e:
            return http_error(e)


class FilesResource(Resource):
    def post(self):
        try:
            service.touch(File(request.form.get('path')))
            return {'status': 'OK'}, 201
        except Exception as e:
            return http_error(e)


def add_api(api, root, name='file'):
    api.add_resource(FileResource, root + '/{0}/<path>'.format(name))
    api.add_resource(FilesResource, root + '/{0}s/<path>'.format(name))
