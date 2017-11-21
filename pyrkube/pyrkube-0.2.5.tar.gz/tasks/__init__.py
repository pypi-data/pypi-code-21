import os
import glob

from invoke import Collection, task

from . import py, docker, test


collections = [py, docker, test]

ns = Collection()
for c in collections:
    ns.add_collection(c)

ns.configure(dict(
    project='pyrkube',
    pwd=os.getcwd(),
    docker=dict(
        user=os.getenv('DOCKER_USER'),
        org=os.getenv('DOCKER_ORG', os.getenv('DOCKER_USER', 'telephoneorg')),
        tag='%s/%s:latest' % (
            os.getenv('DOCKER_ORG', os.getenv('DOCKER_USER', 'telephoneorg')),
            'pyrkube'
        )
    )
))
