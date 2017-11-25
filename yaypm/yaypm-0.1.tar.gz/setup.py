from distutils.core import setup

setup(
    name='yaypm',
    version='0.1',
    packages=[
        'yaypm',
        'yaypm.utils',
        'yaypm.utils.resources',
        'yaypm.utils.tester',
        'yaypm.examples',
    ],
    description='Client lib for yate extmodule',
    author='Daniel Marohn',
    author_email='daniel.marohn@gmail.com',
    url='https://github.com/camillo/yaypm',
    download_url='https://github.com/camillo/yaypm/archive/0.1.tar.gz',
    keywords=['yate', 'extmodule'],
    license='GPL',
    classifiers=[],
)
