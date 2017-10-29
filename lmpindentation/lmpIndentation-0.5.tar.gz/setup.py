from setuptools import setup

setup(
    name='lmpIndentation',
    version='0.5',
    description='Useful package for processing indentation data',
    url='',
    author='Linyuan Shi',
    author_email='Linyuan.shi@outlook.com',
    license='MIT',
    packages=['lmpIndentation'],
    install_requires=['matplotlib', 'numpy'],
    include_package_data=True,
    scripts=['bin/elastic'],
    zip_safe=False)
