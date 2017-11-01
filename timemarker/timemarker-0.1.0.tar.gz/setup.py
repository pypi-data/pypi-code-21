
from setuptools import setup, find_packages

setup(
    name='timemarker',
    packages=find_packages(),
    version='0.1.0',
    author='David Ressman',
    author_email='davidr@ressman.org',
    license='MIT',
    description='Simple arbitrary time measurement tool',
    include_package_data=True,
    url='https://github.com/davidr/python-timemarker',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require=dict(
        test=['coveralls', 'pytest'],
        build=['sphinx', 'pkginfo', 'setuptools-git', 'twine', 'wheel']
    )
)


