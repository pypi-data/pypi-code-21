from setuptools import setup
from distutils.extension import Extension
from distutils.command.sdist import sdist as _sdist


class sdist(_sdist):

    def run(self):
        # make sure the cython-built files are up-to-date
        from Cython.Build import cythonize
        cythonize(Extension('tinex', ['tinex.pyx'],
                            extra_objects=['tinyexpr/tinyexpr.c']))
        _sdist.run(self)


setup(
    name='tinex',
    version='0.2.0.0',
    description='Python wrapper for Tinyexpr',
    author='Arie Bovenberg',
    author_email='a.c.bovenberg@gmail.com',
    url='https://github.com/ariebovenberg/tinex',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

    ],
    ext_modules=[
        Extension('tinex', ['tinex.c'])
    ],
    cmdclass={'sdist': sdist}
)
