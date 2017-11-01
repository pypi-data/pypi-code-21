from distutils.core import setup

setup(
      name='pycra',
      packages=['pycra'],
      version='0.0.1',
      description='Python Challenge Response Authentication with PBKDF2',

      author='Alexander Kleinschmidt (kungalex)',
      author_email='kung4lex@gmail.com',
      license='MIT',

      url='http://github.com/kungalex/pycra',
      download_url='https://github.com/kungalex/pycra/archive/0.0.1.tar.gz',

      install_requires=[
            'pbkdf2helper',
      ],

      keywords=['challenge-response', 'Authentication', 'PBKDF2'],
      classifiers=[],
      )

