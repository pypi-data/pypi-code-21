from setuptools import setup


setup(
    name='Flask-WTF-Polyglot',
    version='0.3',
    url='http://github.com/yggi49/flask-wtf-polyglot',
    license='BSD',
    author='Clemens Kaposi',
    author_email='clemens@kaposi.name',
    description=('Flask-WTF companion library providing `PolyglotForm` for '
                 'polyglot HTML output'),
    packages=['flask_wtf_polyglot'],
    install_requires=[
        'Flask-WTF',
        'WTForms-Polyglot'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
