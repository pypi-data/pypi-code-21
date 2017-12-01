# !/usr/bin/python
from setuptools import setup, find_packages
import nta

setup_requires = []

install_requires = [
    'requests'
]

dependency_links = [
]

setup(
    name='nta',
    version=nta.__version__,
    url='https://github.com/HwangWonYo/naver_talk_sdk',
    license='MIT License',
    description='A Python Library For Naver TalkTalk',
    author='wonyoHwang',
    author_email='hollal0726@gmail.com',
    packages=find_packages(exclude=['tests', 'py2']),
    # include_package_data=True,
    # install_requires=install_requires,
    # setup_requires=setup_requires,
    # dependency_links=dependency_links,
    keywords=['nta', 'navertalk', 'naver', 'chatbot'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)

