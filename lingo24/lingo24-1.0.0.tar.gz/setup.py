from setuptools import find_packages, setup


setup(
    name='lingo24',
    description='Client library for the Lingo24 translation API',
    version='1.0.0',
    url='https://github.com/boltlearning/lingo24',
    author='Bolt Learning',
    author_email='info@boltlearning.com',
    packages=[
        'lingo24',
        'lingo24.business_documents',
    ],
    install_requires=[
        'requests>=2.18',
    ],
    test_suite='nose.collector',
    tests_require=[
        'mock',
        'nose',
        'requests-mock',
    ],
    license='MIT',
)
