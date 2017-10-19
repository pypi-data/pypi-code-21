from distutils.core import setup

setup(
    name="taski",
    version="0.1.14",
    author="Jiale Zhi",
    author_email="vipcalio@gmail.com",
    packages=["app"],
    include_package_data=True,
    url="https://github.com/calio/taski",
    license='MIT',
    description="Taski is a tool to help manage your GTD tasks",
    long_description=open("README.txt").read(),
    scripts=['taski'],
    install_requires=[
        "todoist-python",
        "pytz",
        "tzlocal",
        "pyyaml",
        "coloredlogs",
    ],
)
