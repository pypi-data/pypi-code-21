from flask_restful import Resource
from .model import Path


class PathResource(Resource):
    def get(self, path):
        return {'path': Path(path).abs}


def add_api(api, root, name='path'):
    api.add_resource(PathResource, root + '/{0}/<path>'.format(name))
