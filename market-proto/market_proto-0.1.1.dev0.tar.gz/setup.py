from setuptools import setup, find_packages

#http://python-packaging.readthedocs.io/en/latest/minimal.html
#https://stackoverflow.com/questions/45207128/failed-to-upload-packages-to-pypi-410-gone

setup(
	name='market_proto',
	version='0.1.01dev',
        packages = find_packages(),
        package_data={'': ['*.proto']},
        include_package_data=True,

        setup_requires=[ "setuptools_git >= 0.3", ],

        install_requires=[
            'grpcio',
            'grpcio-tools',
            ],

        author = "Pankaj Garg",
        author_email = "garg.pankaj83@gmail.com",
        description = "SDK to connect to Vaksana Marketplace",
        license = "PSF",
        keywords = "Vaksana Market ProtoBuf",
        url = "http://vaksana.com/sdk#python"
)
