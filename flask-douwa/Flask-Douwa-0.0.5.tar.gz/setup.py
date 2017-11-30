from setuptools import setup


setup(
    name='Flask-Douwa',
    version='0.0.5',
    license='MIT',
    author='jhchen',
    author_email='watasihakamidesu@sina.cn',
    description=u'一个flask插件',
    long_description=__doc__,
    packages=['flask_douwa', 'flask_douwa.rpc', 'flask_douwa.protoparser'],
    zip_safe=False,
    #include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
    ],
    # classifiers=[
    #     'Framework :: Flask',
    #     'Natural Language :: English',
    #     'Environment :: Web Environment',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: MIT License',
    #     'Operating System :: OS Independent',
    #     'Programming Language :: Python',
    #     'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    #     'Topic :: Software Development :: Libraries :: Python Modules'
    # ]
)
