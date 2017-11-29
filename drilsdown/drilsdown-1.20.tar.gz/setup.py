from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
try:
    from jupyterpip import cmdclass 
except:
    import pip, importlib
    pip.main(['install', 'jupyter-pip']); cmdclass = importlib.import_module('jupyterpip').cmdclass

setup( 
    name='drilsdown',
    version='1.20',
    url="https://github.com/Unidata/ipython-IDV",
    author='Unidata',
    author_email='drilsdown@unidata.ucar.edu',
    license="MIT",
    install_requires=['jupyter-pip'],
    packages=['drilsdown'],
    cmdclass=cmdclass('drilsdown','drilsdown/init'),
    description="Jupyter extension for working with the IDV in a notebook ",
    #long_description=read('README.md'),
    scripts=['bin/idv_teleport','bin/ramadda_publish'],
    classifiers=[
    'Development Status :: 4 - Beta',

    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Framework :: IPython',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
]
)

