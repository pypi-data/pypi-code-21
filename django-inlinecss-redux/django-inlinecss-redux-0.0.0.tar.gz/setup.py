from setuptools import setup, find_packages

setup(
    name='django-inlinecss-redux',
    description='A Django app useful for inlining CSS (primarily for e-mails)',
    long_description=open('README.md').read(),
    author='Philip Kimmey',
    author_email='philip@rover.com',
    maintainer='Hugo Osvaldo Barrera',
    maintainer_email='hugo@barrera.io',
    license='BSD',
    url='https://github.com/WhyNotHugo/django-inlinecss-redux',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['html', 'css', 'inline', 'style', 'email'],
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Environment :: Other Environment',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    install_requires=[
        'Django',
        'pynliner',
        'mock',
    ],
)
