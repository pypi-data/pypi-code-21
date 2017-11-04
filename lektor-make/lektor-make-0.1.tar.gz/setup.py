from setuptools import setup

setup(
    name='lektor-make',
    version='0.1',
    author='Barnaby Shearer',
    author_email='b@zi.is',
    url='http://github.com/BarnabyShearer/lektor-make',
    license='MIT',
    py_modules=['lektor_make'],
    description='Run `make lektor` for custom build systems.',
    entry_points={
        'lektor.plugins': [
            'make = lektor_make:MakePlugin',
        ]
    }
)
