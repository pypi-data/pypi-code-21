from distutils.core import setup

setup(
    name='flask-blueprint',
    version='1.0.0',
    description='Flask blueprint generator',
    author='Jeffrey Marvin Forones',
    author_email='aiscenblue@gmail.com',
    url='https://github.com/aiscenblue/flask-blueprint',
    py_modules=['core', 'package_extractor', 'module_router'],
    install_requires=[
        # list of this package dependencies
    ],
    entry_points=None
)