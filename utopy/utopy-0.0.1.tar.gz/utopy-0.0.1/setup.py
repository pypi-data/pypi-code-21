from setuptools import setup

setup(
    name='utopy',
    version='0.0.1',
    py_modules=['utopy'],
    url='http://github.com/emre/utopy',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='Utopian curation bot',
    entry_points={
        'console_scripts': [
            'utopy = utopy.utopy:main',
        ],
    },
    install_requires=["dataset", "steem==0.18.103", "pymysql", "requests"]
)
