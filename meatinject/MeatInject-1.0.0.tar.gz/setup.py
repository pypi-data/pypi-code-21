from setuptools import setup

setup(
    name='MeatInject',
    version='1.0.0',
    packages=['meatinject'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description="MIT",
    keywords='meatspin meat spin omg lol',
    long_description=open('README.md').read(),
    url='https://github.com/antitree/meatinject',
    python_requires='>=2.7, <4',
    entry_points={
        'console_scripts': ['meatinject=meatinject:main', ],
        },
)
