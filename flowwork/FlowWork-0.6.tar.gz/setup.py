

from setuptools import setup, find_packages


setup(name='FlowWork',
    version='0.6',
    description='a simple way to use mongo db, let db like dict',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    scripts=['install.sh'],
    install_requires=['SocialKit'],
)


