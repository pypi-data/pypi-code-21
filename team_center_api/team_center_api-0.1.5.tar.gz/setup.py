from setuptools import setup, find_packages

setup(
    name="team_center_api",
    version='0.1.5',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires=['requests'],
    url="https://github.com/dantezhu/team_center",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="team center api",
)
