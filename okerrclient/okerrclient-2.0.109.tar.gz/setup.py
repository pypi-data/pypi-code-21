from setuptools import setup

setup(name='okerrclient',
    version='2.0.109',
    description='client for okerr cloud monitoring system',
    url='http://okerr.com/',
    author='Yaroslav Polyakov',
    author_email='xenon@sysattack.com',
    license='MIT',
    packages=['okerrclient'],
    scripts=['scripts/okerrclient'],
    data_files = [
        ('okerrclient/conf',['data/conf/okerrclient.conf']),
        ('okerrclient/init.d', ['data/init.d/okerrclient']),
        ('okerrclient/systemd',['data/systemd/okerrclient.service']),
    ], 
    install_requires=['six', 'pyping', 'requests', 'psutil', 'evalidate', 'python-daemon', 'configargparse', 'fasteners'],
    include_package_data = True,
    zip_safe=False
)    

