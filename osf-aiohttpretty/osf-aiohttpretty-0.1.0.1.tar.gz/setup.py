from setuptools import setup, find_packages


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n') for l in f if l.strip('\n') and not l.startswith('#')]


requirements = parse_requirements('requirements.txt')

setup(
    name='osf-aiohttpretty',
    version='0.1.0.1',
    description='AioHTTPretty',
    author='Center for Open Science',
    author_email='contact@cos.io',
    url='https://github.com/CenterForOpenScience/aiohttpretty',
    packages=find_packages(exclude=('tests*', )),
    package_data={
        'aiohttpretty': ['requirements.txt'],
    },
    py_modules=['aiohttpretty'],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
