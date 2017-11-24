from setuptools import setup
from setuptools import find_packages
import os

version = os.environ['VERSION']

extras_require = {
    'awscli': ['cloudtoken-plugin.awscli_exporter'],
}

all_extras = [item for sub in extras_require.values() for item in sub]

extras_require['all'] = all_extras

setup(
    name='cloudtoken',
    version=version,
    description='Command line utility for authenticating with public clouds.',
    url='https://bitbucket.org/atlassian/cloudtoken/',
    author='Atlassian Cloud Engineering',
    author_email='cloud-team@atlassian.com',
    license='Apache',
    scripts=['bin/cloudtoken', 'bin/cloudtoken.cmd', 'bin/cloudtoken_proxy.sh', 'bin/awstoken'],
    zip_safe=False,
    install_requires=[
        "Flask>=0.12",
        "watchdog>=0.8.3",
        "schedule>=0.4.2",
        "cloudtoken-plugin.shell-exporter",
        "cloudtoken-plugin.json-exporter",
        "cloudtoken-plugin.saml",
    ],
    extras_require=extras_require,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'cloudtoken': ['proxy.py'],
    },
    data_files=[('share/cloudtoken/shell_additions', ['shell_additions/bashrc_additions',
                                                      'shell_additions/fishconfig_additions',
                                                      'shell_additions/unset_cloudtoken.fish']),
                ('share/cloudtoken/configs', ['configs/config.yaml', 'configs/proxy.yaml'])],
)
