from setuptools import setup
setup(
    name='lp_accounts',
    packages=['lp_accounts'],
    package_data={'lp_accounts': ['migrations/*', 'validators/*']},
    version='2.0.1',
    description='REST Framework for User Accounts',
    author='Jim Simon',
    author_email='hello@launchpeer.com',
    url='https://github.com/Launchpeer/django-rest-account',
    download_url='https://github.com/Launchpeer/django-rest-account/archive/master.tar.gz',
    keywords=[],
    classifiers=[],
    python_requires='>=3',
    install_requires=[
        'django',
        'django-rest-framework',
        'django-templated-email',
        'parameterized',
        'python-social-auth'
        'pyyaml',
        'rest-condition',
        'rest-framework-generic-relations',
        'requests',
        'django-rest-framework-social-oauth2',
    ],
)
