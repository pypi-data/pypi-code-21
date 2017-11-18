import sys
from setuptools import setup

args = ' '.join(sys.argv).strip()
if not any(args.endswith(suffix) for suffix in ['setup.py check -r -s', 'setup.py sdist']):
    raise ImportError('Did you mean to install aws-encryption-sdk-cli?',)

setup(
    author='Amazon Web Services',
    author_email='aws-cryptools@amazon.com',
    classifiers=['Development Status :: 7 - Inactive'],
    description='Did you mean to install aws-encryption-sdk-cli?',
    long_description='\nThis package has been parked by Amazon Web Services to protect you against packages\nadopting names that might be common mistakes when looking for ours. You probably\nwanted to install aws-encryption-sdk-cli. For more information, see http://aws-encryption-sdk-cli.readthedocs.io/en/latest/.',
    name='aws-encrpytion-cli',
    url='http://aws-encryption-sdk-cli.readthedocs.io/en/latest/',
    version='0.0.1'
)
