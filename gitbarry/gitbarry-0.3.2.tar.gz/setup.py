from setuptools import setup, find_packages

requires = [
    'sh==1.11',
    'requests==2.11.0',
]

test_requires = requires

setup(
    name='gitbarry',
    version='0.3.2',
    packages=find_packages(),
    url='https://github.com/a1fred/git-barry',
    license='MIT',
    author='a1fred',
    author_email='demalf@gmail.com',
    description='Customizable git workflow extension',
    install_requires=requires,
    tests_require=test_requires,
    test_suite="tests",
    entry_points={
        'console_scripts': ['git-barry=gitbarry.main:run'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: System :: Software Distribution',
    ],
)
