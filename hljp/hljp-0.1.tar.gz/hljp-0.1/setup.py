from setuptools import setup

requires = [
    'requests'
]

tests_require = [
    'pytest',
    'pytest-cov',
    'tox'
]


setup(
    name='hljp',
    version='0.1',
    description='Lets you post to your 401 learning journal from the terminal',
    author='H. Cody Dibble',
    author_email='hcodydibble@gmail.com',
    license='MIT',
    extras_require={
        'test': tests_require,
    },
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'post=hljp.poster:main',
        ],
    },
)
