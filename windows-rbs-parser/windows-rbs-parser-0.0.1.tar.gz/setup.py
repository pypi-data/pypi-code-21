from setuptools import setup

setup(
    name="windows-rbs-parser",
    description="Python library/tool which is able to parse .rbs files used by the windows diagnostics framework",
    version="0.0.1",
    author="BlueC0re",
    author_email="info@bluec0re.eu",
    license="MIT",
    url="https://github.com/bluec0re/windows-rbs-parser",
    packages=["rbs_parser"],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    install_requires=[
        'helperlib>=0.4.1'
    ],
    entry_points={
        'console_scripts': [
            'rbs-parser = rbs_parser:main'
        ]
    }
)
