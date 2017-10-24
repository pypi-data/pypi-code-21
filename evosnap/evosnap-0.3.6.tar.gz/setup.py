from distutils.core import setup

setup(
    name='evosnap',
    packages=[
        'evosnap',
        'evosnap.service_information',
        'evosnap.transactions',
        'evosnap.transactions.base',
        'evosnap.transactions.bankcard',
        'evosnap.merchant_applications',
    ],
    version='0.3.6',
    description='Python 3 package that integrates with EVO Snap* Commerce Web Services API',
    author='Javier Ros Honduvilla',
    author_email='javier.ros.honduvilla@gmail.com',
    url='https://github.com/Zertifica/evosnap',
    download_url='https://github.com/Zertifica/evosnap/tarball/0.1',
    keywords=['popular payments', 'tpv', 'snap'],
    classifiers=[],
)
