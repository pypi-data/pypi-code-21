from setuptools import setup, find_packages

setup(name='dataClay',
      version='0.7.0',
      install_requires=["enum34",
                        "pyyaml",
                        "lru-dict",
                        "jinja2",
                        "decorator",
                        "grpcio>=1.7.0rc1",
                        "grpcio-tools>=1.7.0rc1",
                        "protobuf",
                        ],
      description='Python library for dataClay',
      packages=find_packages(),
      package_data={
        # All .properties files are valuable "package data"
        '': ['*.properties'],
      },
      )
