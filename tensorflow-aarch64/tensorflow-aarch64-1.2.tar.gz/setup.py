from distutils.core import setup
setup(
  name = 'tensorflow-aarch64',
  packages = ['tensorflow-aarch64'], # this must be the same as the name above
  version = '1.2',
  description = 'Tensorflow r1.2 for aarch64[arm64,pine64] CPU only.',
  author = 'Tirdtoon Samaroek',
  author_email = 'tirdtoon@gmail.com',
  url = 'http://ai.2psoft.com/tensorflow/pine64/tensorflow-aarch64/', # use the URL to the github repo
  download_url = 'http://ai.2psoft.com/tensorflow/pine64/tensorflow-1.2.1-cp27-cp27mu-linux_aarch64.whl', # I'll explain this in a second
  keywords = ['tensorlfow', 'aarch64', 'arm64'], # arbitrary keywords
  classifiers = [],
)
