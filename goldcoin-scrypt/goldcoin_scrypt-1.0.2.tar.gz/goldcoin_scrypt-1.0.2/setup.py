from distutils.core import setup, Extension

goldcoin_scrypt_module = Extension('goldcoin_scrypt',
                               sources = ['goldcoin_scrypt/scryptmodule.c',
                                          'goldcoin_scrypt/scrypt.c'],
                               include_dirs=['/usr/include/python3.5/'])

setup (
    name = 'goldcoin_scrypt',
    version = '1.0.2',
    description = 'Bindings for scrypt proof of work used by Goldcoin',
    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    ext_modules = [goldcoin_scrypt_module]
)