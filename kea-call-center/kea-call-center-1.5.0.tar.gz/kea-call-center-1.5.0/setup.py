import json
from distutils.core import setup

with open('package.json') as data_file:
    package = json.load(data_file)

name = package["name"]
version = package["version"]

setup(
    name=name,
    packages=[name],  # this must be the same as the name above

    package_dir={name: "."},
    package_data={
        name: [
            "*.json",
            "dist/*.css",
            "dist/*.js",
            "lib/*.css",
            "lib/*.js"
        ]
    },

    version=version,
    description='Frontend files package for keacloud-call-center',
    author='Diwank Tomer',
    author_email='diawnk@kea.cloud',
    url='https://github.com/keacloud/new-call-center',  # use the URL to the github repo
    keywords=['kea']
)
