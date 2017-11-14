from distutils.core import setup


if __name__ == '__main__':
    setup(
        name='superpadova',
        version='0.0.1',
        author='Bo Zhang',
        author_email='bozhang@mpia.de',
        # py_modules=['bopy','spec','core'],
        description='PADOVA isochrone interpolator.',  # short description
        license='MIT',
        # install_requires=['numpy>=1.7','scipy','matplotlib','nose'],
        url='http://github.com/hypergravity/superpadova',
        classifiers=[
            "Development Status :: 6 - Mature",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.6",
            "Topic :: Scientific/Engineering :: Astronomy",
            "Topic :: Scientific/Engineering :: Physics"],
        package_dir={'superpadova/': ''},
        packages=['superpadova',],
        # package_data={'bopy/data': [''],
        #               "":          ["LICENSE"]},
        # include_package_data=True,
        requires=['numpy', 'scipy', 'matplotlib', 'astropy', 'ezpadova']
    )
