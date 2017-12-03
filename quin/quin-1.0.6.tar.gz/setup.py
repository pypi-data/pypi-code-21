from setuptools import setup

setup(
    name='quin',
    version='1.0.6',
    url='https://github.com/journey-ad/quin',
    author='journey.ad',
    author_email='journey.adc@gmail.com',
    description=('rua！真实终端大秦话'),
    license='MIT',
    packages=['quin'],
    package_data={'quin': ['static/*.txt']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    entry_points={'console_scripts': ['quin = quin.core:main']},
)
