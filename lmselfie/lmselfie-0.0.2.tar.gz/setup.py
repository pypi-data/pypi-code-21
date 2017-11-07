from setuptools import setup

setup(
    name='lmselfie',
    version='0.0.2', # Cada vez que lo subis lo tenes que incrementar
    author='Lucas Saavedra',
    description='Software para cabina de selfie',
    author_email='saavedralucasemanuel@gmail.com',
    packages=['lmselfie'],
    scripts=[],
    url='https://bitbucket.org/TuTa1612/lmselfie',
    license=open('LICENSE.txt').read(), #lazy programer is lazy
    long_description=open('README.txt').read(), # idem
    install_requires=[], # no admite repos de GIT solo paquetes
    entry_points={
        'console_scripts': ['lmselfie = lmselfie.__init__']#:main']
    },
    package_data={
        'lmselfie': ['templates/*'], # todos los != .py
    },
)
