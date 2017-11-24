from setuptools import setup, find_packages

NAME = 'batchcompute-sge'

VERSION = '1.3.1'

setup(
    name = NAME,
    version =  VERSION,
    keywords = ('batchcompute-sge','bcs-sge','sge'),
    description = 'Alibaba Cloud BatchCompute SGE command line interface',
    license = 'MIT License',

    url = 'http://www.aliyun.com/product/batchcompute',
    author = 'guangchun.luo',
    author_email = 'guangchun.luo@alibaba-inc.com',

    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    package_data={'': ['bin/sge_master_watchdog']},

    platforms = 'any',

    install_requires = ['aliyun-python-sdk-ecs','batchcompute==2.0.9a2','oss2','terminal'],
    entry_points='''
        [console_scripts]
        bccluster=batchcompute_sge.bin.bccluster:main
        bcc=batchcompute_sge.bin.bccluster:main
        sge_master_watchdogd=batchcompute_sge.bin.sge_master_watchdog:main
        sge_execd_watchdogd=batchcompute_sge.bin.sge_execd_watchdog:main
        sge_bootstrap=batchcompute_sge.bin.sge_bootstrap:main
    '''
)
