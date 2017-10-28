from setuptools import setup

setup(name='kms_encrypter',
      version='0.1.3',
      description='Encrypt using AWS KMS',
      install_requires= ['boto3'],
      url='https://github.com/haradashinya/kms_encrypter',
      author='furodrive',
      author_email='haradashinya@gmail.com',
      license='MIT',
      packages=['kms_encrypter'],
      zip_safe=False)
