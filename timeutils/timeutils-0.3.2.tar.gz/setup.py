import setuptools
import timeutils

# main project configurations is loaded from setup.cfg by setuptools
assert setuptools.__version__ > '30.3', "setuptools > 30.3 is required"

# add more parameters to configuration
cfg = setuptools.config.read_configuration("setup.cfg")
download_url = cfg["metadata"]["url"] + "/repository/v" + \
               timeutils.__version__ + "/archive.tar.gz"

# setup() call
setuptools.setup(download_url=download_url)
