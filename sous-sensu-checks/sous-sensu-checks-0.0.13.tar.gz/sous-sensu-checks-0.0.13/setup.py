from setuptools import setup, find_packages

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

setup(
    name="sous-sensu-checks",
    description="Run checks against apps defined in a Sous global manifest.",
    long_description=open('README.rst').read(),
    version="0.0.13", # NB: Version is duplicated in sous-sensu-checks.
    packages=find_packages(),
    author='OpenTable Sous Team',
    author_email='sous@opentable.onmicrosoft.com',
    url="https://github.com/opentable/sous-sensu-checks",
    scripts=["sous-sensu-checks"],
    license="Apache 2",
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: Apache Software License',
      'Topic :: System :: Monitoring',
      'Topic :: System :: Networking :: Monitoring'
    ]
)
