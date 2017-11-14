from setuptools import setup

setup(
    name='lmselfie',
    version='0.0.12', # Cada vez que lo subis'time', 'picamera' lo tenes que incrementar
    author='Lucas Saavedra',
    description='Software para cabina de selfie',
    author_email='saavedralucasemanuel@gmail.com',
    packages=['lmselfie'],
    scripts=[],
    url='https://bitbucket.org/TuTa1612/lmselfie',
    license='licencia',
    long_description='Software para cabina de selfie',
    install_requires=['gpiozero', 'PIL', 'time', 'picamera>=1.13'], # no admite repos de GIT solo paquetes
    entry_points={
        'console_scripts': ['lmselfie = lmselfie']
    },
    package_data={
        'lmselfie': ['templates/*'], # todos los != .py
    },
)
