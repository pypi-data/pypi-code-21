from setuptools import setup

# python setup.py build
# python setup.py sdist
# sudo python setup.py install
# twine upload dist/*

setup(
    name='falkus',
    version='1.2',
    description='Automation for quick setup of AWS SAM application with Python Lambda',
    url='https://gitlab.com/daniele.rigato.amz/falkus',
    author='Daniele Rigato',
    author_email='daniele.rigato@gmail.com',
    license='GNU GPL v3',
    classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2.7',
    ],
    keywords='aws lambda SAM serverless',
    scripts=['falkus'],
    packages=['falkuslib', 'falkustest'],
    install_requires=['jsonschema', 'requests', 'boto3']
)
