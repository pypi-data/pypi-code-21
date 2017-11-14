from setuptools import setup


setup(
    name='WTForms-Polyglot',
    version='0.3',
    url='http://github.com/yggi49/wtforms-polyglot',
    license='BSD',
    author='Clemens Kaposi',
    author_email='clemens@kaposi.name',
    description=('WTForms companion library to provide polyglot HTML '
                 '(i.e., XML-compatible) output'),
    packages=['wtf_polyglot'],
    install_requires=['WTForms'],
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
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
