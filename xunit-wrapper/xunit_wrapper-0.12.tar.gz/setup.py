from setuptools import setup


setup(
    name="xunit_wrapper",
    version='0.12',
    description='Wrap python functions with a decorator to handle building XUnit reports',
    author='E Rasche',
    author_email='esr@tamu.edu',
    license='GPL-3.0',
    install_requires=['junit-xml==1.7', 'future'],
    url='https://github.com/TAMU-CPT/xunit-python-decorator',
    packages=["xunit_wrapper"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        ],
    include_package_data=True,
)
