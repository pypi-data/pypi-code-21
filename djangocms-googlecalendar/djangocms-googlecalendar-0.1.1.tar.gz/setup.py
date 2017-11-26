

from setuptools import find_packages, setup

from djangocms_googlecalendar import __version__


REQUIREMENTS = [
    'django-cms',
    # 'django-filer'
]


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


setup(
    name='djangocms-googlecalendar',
    version=__version__,
    author='Ben Miller',
    author_email='mail@benkmiller.com',
    url='https://github.com/benjiyamin/djangocms-googlecalendar',
    license='GNU General Public License v3 (GPLv3), see LICENSE.md',
    description=('Adds Google Calendar plugins to django CMS.'),
    long_description=open('README.md').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)

