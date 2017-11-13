from setuptools import setup, find_packages

setup(
        name = 'pyrses',
        version = '0.0.2',
        description = 'ncurses based TUI framwork',
        url = 'https://github.com/jeremyCloud/pyrses.git',
        author = 'sloud',
        author_email = 'sloudly2@gmail.com',
        license = 'MIT',
        classifiers = [
            'Development Status :: 1 - Planning',
            'Environment :: Console',
            'Intended Audience :: Developers',
            ],
        keywords = 'TUI framework ncurses curses terminal',
        packages = find_packages(),
        install_requires = ['pyyaml'],
        python_requires = '>=3.5',
        package_data = {
            'pyrses': ['templ/*']
            },
        entry_points = {
            'console_scripts': [
                'pyrses=pyrses.pyrses:cli',
                ],
            },

        zip_safe = False,
        )

