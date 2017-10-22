

from setuptools import setup, find_packages


setup(name='mroylib_min',
    version='1.3.2',
    description='some libs',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['redis', 'pymysql', 'bs4','requests','termcolor','bson','simplejson','pysocks'],

)


