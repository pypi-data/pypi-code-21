from setuptools import setup, find_packages

install_requires = [
    'requests',
    'jsonpickle',
    'urllib3',
    'sseclient-py'
]
dependency_links = []
setup_requires = []
tests_require = ['unittest', 'io']

setup(
    name='falkonryclient',
    version='1.0.4',
    author='Falkonry Inc',
    author_email='info@falkonry.com',
    license='MIT',
    url='https://github.com/Falkonry/falkonry-python-client',
    download_url = 'https://github.com/Falkonry/falkonry-python-client/tarball/1.0.4',
    description='Falkonry Python Client to access Condition Prediction APIs',
    long_description='Falkonry python client to access Condition Prediction APIs',
    packages=['falkonryclient', 'falkonryclient.helper', 'falkonryclient.helper.models', 'falkonryclient.service'],
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require={
        'test': ['unittest', 'io'],
        'all': install_requires + tests_require
    },
    dependency_links=dependency_links,
    zip_safe=False,
    include_package_data=True,
    keywords='falkonry falkonryclient conditionprediction'
)
