from setuptools import setup

setup(
    name='moonshot-algo',
    packages=['moonshot_algo'],
    version='1.0.9',
    description='core python algo',
    author='shai kazaz',
    author_email='shai@moonshot.co.il',
    install_requires=['pandas', 'mongoengine'],
    url='https://github.com/moonshot-marketing/algo-py-core',  # use the URL to the github repo
    zip_safe=False,
    classifiers=[],
)
