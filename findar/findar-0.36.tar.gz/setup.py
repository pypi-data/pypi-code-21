from setuptools import setup, find_packages

setup(name='findar',
      version='0.36',
      description='Financial Datareader (findar)',
      long_description='Financial Datareader provides data solutions to quantitative trading and \
      backtesting.Currently provides up-to-date index constituent lists, full ETF lists \
      trading boardlots, fundamental informations, Libor rates etc, for both US and HK market.',
      url='https://github.com/wwengm/findar',
      author='wwengm',
      license='MIT',
      zip_safe=False,
      keywords='financial data',
      packages=find_packages(),
      install_requires=['pandas', 'pandas_datareader', 'beautifulsoup4', 'requests', 'quandl', 'tushare'],)
