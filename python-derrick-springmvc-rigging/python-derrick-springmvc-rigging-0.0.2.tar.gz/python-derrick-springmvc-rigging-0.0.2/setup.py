from setuptools import setup, find_packages

setup(
    name='python-derrick-springmvc-rigging',
    version='0.0.2',
    description="derrick rigging for springmvc project",
    keywords='',
    author="injektto",
    author_email="injekt.to@hotmail.com",
    url="https://github.com/injekt/derrick-springmvc-rigging",
    py_modules=['derrick'],
    include_package_data=True,
    install_requires=[
        'jinja2',
        'docopt',
        'whaaaaat',
        'pychalk',
        'simplejson',
        'setuptools-git'
    ],
    entry_points='''
        [console_scripts]
        derrick=derrick.derrick:main
    ''',
    packages=find_packages()
)
