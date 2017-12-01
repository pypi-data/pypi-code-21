from setuptools import setup
from setuptools import find_packages

setup(
    name='apex-cli',
    version='0.0.5',
    description='Command-line interface of apex(serverless framework)',
    author='finwhale',
    author_email='waitingforqodot@gmail.com',
    url='https://github.com/finwhale/apex-cli',
    download_url='https://github.com/finwhale/apex-cli/archive/master.zip',
    packages=find_packages(),
    package_data={
        'src': ['templates/*.tmpl', 'templates/**/*.tmpl'],
    },
    python_requires='>=3.6',
    install_requires=[
        'click==6.7',
        'Jinja2==2.10',
    ],
    entry_points={
        'console_scripts': [
            'apex-cli=src.apex_cli:apex_cli'
        ]
    }
)
