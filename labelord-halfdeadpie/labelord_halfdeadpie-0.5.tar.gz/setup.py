from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = ''.join(f.readlines())


setup(
    name='labelord_halfdeadpie',
    version='0.5',
    description='Replicate Github Labels',
    long_description=long_description,
    author='Simon Stefunko',
    author_email='s.stefunko@gmail.com',
    keywords='labels, labelord, github, flask, web',
    license='Public Domain',
    url='https://github.com/HalfDeadPie/labelord_halfdeadpie',
    packages=['labelord'],
    package_data = {'labelord': ['templates/*.html']},
    python_requires='~=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Framework :: Flask',
        'Environment :: Console',
        'Environment :: Web Environment'
        ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'labelord = labelord.unity:main',
        ],
    },
    install_requires=['Flask', 'click>=6', 'requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'betamax', 'flexmock'],
)