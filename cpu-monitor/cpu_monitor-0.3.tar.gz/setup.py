from setuptools import setup

setup(name='cpu_monitor',
      packages=['cpu_monitor'],
      version='0.3',
      description='Cpu monitoring and burning tool',
      author='yotabits',
      author_email='tkostas75@gmail.com',
      license='MIT',
      url='https://github.com/yotabits/cpu_monitor',
      #download_url='https://github.com/yotabits/cpu_monitor/archive/0.1.tar.gz',
      scripts=['bin/cpu_monitor'],
      keywords='monitoring cpu',
      install_requires=[
          'py-cpuinfo',
          'plotly',
          'colorama',
          'dash',
          'dash_renderer',
          'dash_core_components',
          'dash_html_components'
      ],
        classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        ],
      zip_safe=False)
