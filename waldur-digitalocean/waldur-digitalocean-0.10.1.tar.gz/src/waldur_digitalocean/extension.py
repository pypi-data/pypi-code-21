from __future__ import unicode_literals

from nodeconductor.core import NodeConductorExtension


class DigitalOceanExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'waldur_digitalocean'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def get_cleanup_executor():
        from .executors import DigitalOceanCleanupExecutor
        return DigitalOceanCleanupExecutor
