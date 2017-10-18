from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_requires = [line for line in f if line and line[0] not in '#-']

with open('test-requirements.txt') as f:
    tests_require = [line for line in f if line and line[0] not in '#-']

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
]

setup(
    name='ocder',
    version='0.1.0',
    url='https://github.com/yedpodtrzitko/ocder',
    author='yedpodtrzitko',
    author_email='yed@vanyli.net',
    license='MIT',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'ocder=ocder.run:run'
        ]
    }
)
