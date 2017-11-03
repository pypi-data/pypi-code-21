from setuptools import setup

def readme():
    with open('README.md') as readme:
        return readme.read()

setup(
        name = 'pydotask',
        version = '0.4.2',
        description = 'PyDo is a CLI Application to keep you on track with your tasks and projects',
        long_description = readme(),
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 3.5',
            'Topic :: Office/Business :: Scheduling'
            ],
        keywords = 'utilities office schedule task reminder',
        url = '',
        author = 'Abhishta Gatya',
        author_email = 'abhishtagatya@yahoo.com',
        packages = ['task_mod','task_mod.styles'],
        entry_points = {
            'console_scripts' : ['pydo=task_mod.pydo:main'],
            },
        python_requires = '>=3',
        include_package_data = True,
        zip_safe = False
        )
