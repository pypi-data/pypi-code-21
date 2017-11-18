from setuptools import setup

setup(
        name='twoprocessmodel',
        version='0.0.1',
        packages=['twoprocessmodel'],
        url='https://gitlab.com/fwahl/twoprocessmodel',
        license='MIT',
        author='Florian Wahl',
        author_email='florian.wahl@gmail.com',
        description='An implementation of the two Process Model for circadian biology.',
        setup_requires=['pytest-runner'],
        tests_require=['pytest', 'numpy'],
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Bio-Informatics',

            # Pick your license as you wish (should match "license" above)
             'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        keywords='two process model, circadian',
        py_modules=["circadianProcess", "noiseProcess", "homeostaticProcess"],
)
