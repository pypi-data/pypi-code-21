from distutils.core import setup

setup(
    name='steamstoreprice',
    packages=['steamstoreprice'],
    package_dir={'steamstoreprice': 'steamstoreprice'},
    version='0.2',
    install_requires=['requests', 'beautifulsoup4'],
    description='Find the price on Steam Store from url',
    author='Alessandro Sbarbati',
    author_email='miriodev@gmail.com',
    url='https://github.com/Mirio/steamstoreprice',
    download_url='https://github.com/Mirio/steamstoreprice/tarball/0.1',
    keywords=['Steam', 'Steam Price', 'Steam Store', "steamstoreprice"],
    license='BSD',
    classifiers=["License :: OSI Approved :: BSD License", "Programming Language :: Python :: 3",
                 "Topic :: Software Development :: Libraries :: Python Modules", "Topic :: Utilities"],
)
