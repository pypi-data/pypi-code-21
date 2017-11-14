import setuptools

version = '0.5.0'

setuptools.setup(
    name='ctec_consumer',
    version=version,
    packages=setuptools.find_packages(),
    author='ZhangZhaoyuan',
    author_email='zhangzhy@chinatelecom.cn',
    url='http://www.189.cn',
    description='189 rabbitMQ consumer',
    install_requires=['gevent==1.2.2', 'pika==0.11.0', 'kazoo==2.4.0', 'psutil==5.3.1']
)
