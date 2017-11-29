from setuptools import setup
import os

version = os.environ['VERSION']

setup(
    name='cloudtoken-plugin.shell_exporter',
    version=version,
    description='Shell exporter for cloudtoken.',
    url='https://bitbucket.org/atlassian/cloudtoken',
    author='Atlassian Cloud Engineering',
    author_email='cloud-team@atlassian.com',
    license='Apache',
    py_modules=['cloudtoken_plugin.export_credentials_shell'],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[],
)
