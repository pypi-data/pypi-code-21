from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name='ADwin',
    version='0.16.0',
    platforms=['linux2, win32, darwin'],
    description='ADwin API wrapper',
    long_description=long_description,
    maintainer='Jaeger Computergesteuerte Messtechnik GmbH',
    author='Markus Borchers',
    author_email='info@ADwin.de',
    url='http://www.ADwin.de',
    license='''Apache License 2.0''',
    py_modules=['ADwin']
)
