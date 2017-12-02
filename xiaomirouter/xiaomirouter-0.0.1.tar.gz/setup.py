from setuptools import setup

setup(
    name='xiaomirouter',
    version='0.0.1',
    description='Deliver info from Xiaomi Router products.',
    url='https://github.com/RiRomain/python-xiaomi-router/',
    license='MIT',
    author='RiTomain',
    author_email='romain.rinie@googlemail.com',
    packages=['xiaomirouter', 'xiaomirouter.client', 'xiaomirouter.status'],
    install_requires=['requests', 'httpretty', ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ]
)
