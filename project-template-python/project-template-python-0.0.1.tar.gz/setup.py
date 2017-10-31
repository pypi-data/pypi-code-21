from setuptools import setup, find_packages

import project_template_python

setup(
        name='project-template-python',
        version=project_template_python.__version__,
        packages=find_packages(),
        description='remove watermark',
        author='caviler',
        author_email='caviler@gmail.com',
        license='BSD',
        url='https://github.com/sixquant/project-template-python',
        keywords='remove watermark',
        install_requires=['numpy', 'pandas'],
        classifiers=['Development Status :: 3 - Alpha',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.4',
                     'Programming Language :: Python :: 3.5',
                     'Programming Language :: Python :: 3.6',
                     'License :: OSI Approved :: BSD License'],
)
