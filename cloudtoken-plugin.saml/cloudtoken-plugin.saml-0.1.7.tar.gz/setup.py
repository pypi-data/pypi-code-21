from setuptools import setup
import os

version = os.environ['VERSION']

setup(
    name='cloudtoken-plugin.saml',
    version=version,
    description='SAML plugin for cloudtoken.',
    url='https://bitbucket.org/atlassian/cloudtoken',
    author='Atlassian Cloud Engineering',
    author_email='cloud-team@atlassian.com',
    license='Apache',
    py_modules=['cloudtoken_plugin.saml'],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        "boto3>=1.4.0",
        "cloudtoken",
        ],
)
