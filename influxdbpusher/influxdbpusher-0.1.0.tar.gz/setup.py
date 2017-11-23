import setuptools

setuptools.setup(
    name="influxdbpusher",
    version="0.1.0",
    url="https://github.com/GambitResearch/influxdbpusher",

    author="Gustavo Carneiro",
    author_email="gjcarneiro@gmail.com",

    description="Minimal and smart pusher of samples to InfluxDB for asyncio programs",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=['aiohttp>=2.0'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
