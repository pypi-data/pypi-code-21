import codecs
from distutils.core import setup
import os.path as path

install_requires = ['requests']
cwd = path.dirname(__file__)
version = '0.1.0'

setup(
    name='dispatchsdk',
    author='Jason Raede',
    author_email='jason@dispatch.me',
    version=version,
    license='MIT',
    description='SDK for interacting with the Dispatch platform',
    url='https://github.com/DispatchMe/python-sdk',
    packages=['dispatchsdk'],
    include_package_data=True,
    platforms='ANY',
    requires=['requests', 'urllib3']
)
