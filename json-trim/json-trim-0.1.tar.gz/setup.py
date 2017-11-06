from distutils.core import setup
from distutils.core import Command



class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(DATABASES={'default': {'NAME': ':memory:',
            'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=('json-trim',))
        from django.core.management import call_command
        import django

        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', 'json-trim')


setup(name='json-trim',
    version='0.1',
    packages=['jsonfield-trim'],
    license='MIT',
    author='fahad',
    author_email='fahadsiddiqui707@gmail.com',
    url='https://github.com/fahadsiddiqui007',
    description='A reusable Django field that allows you to store validated JSON in your model.',
    long_description=open("README.txt").read(),
    install_requires=['Django >= 1.4.3'],
    tests_require=['Django >= 1.4.3'],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Framework :: Django',
    ],
)
