from importlib.util import find_spec

import setuptools


def main():
    setuptools.setup(
        name='shuup-attrim',
        version='0.9.0.3',
        description='Multi-value attributes addon for Shuup E-Commerce Platform',
        url='https://gitlab.com/nilit/shuup-attrim',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Framework :: Django :: 1.9',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Office/Business',
        ],
        keywords=['shuup', 'attributes'],
        packages=setuptools.find_packages(),
        include_package_data=True,
        entry_points={'shuup.addon': 'attrim=attrim'},
        cmdclass=_get_commands(),
        install_requires=[
            'shuup >= 1.1.0, < 2',
            'psycopg2 >= 2.6.2, < 3',
            'shuup-testutils >= 0.10, < 0.11',
            'shuup-utils >= 0.4, < 0.5',
        ],
    )


def _get_commands() -> dict:
    is_shuup_installed = find_spec('shuup') is not None
    is_shuup_utils_installed = find_spec('shuup_utils') is not None
    if is_shuup_installed and is_shuup_utils_installed:
        import shuup_setup_utils
        from shuup_utils.setuptools.commands import build_static
        
        shuup_commands = shuup_setup_utils.COMMANDS
        project_commands = {'build_static': build_static}
        return {**shuup_commands, **project_commands}
    else:
        return {}


if __name__ == '__main__':
    main()
