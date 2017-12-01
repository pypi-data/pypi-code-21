import os

import click
import jinja2


@click.group()
def apex_cli():
    pass


def validate_name(context, params, value):
    directory = f'functions/{value}'
    if os.path.exists(directory):
        raise click.BadParameter(f'The function name {value} already exists')
    return value


def validate_runtime(context, params, value):
    available_runtime = ['python3.6']
    if value not in available_runtime:
        runtimes = ', '.join(available_runtime)
        raise click.BadParameter(f'{value} is a wrong runtime. Available runtimes are {runtimes}')
    return value


def _ext(runtime):
    return {
        'python3.6': 'py',
    }[runtime]


@apex_cli.command()
@click.option('--name', '-n', prompt='Your function name', type=str, callback=validate_name)
@click.option('--description', '-d', prompt='Your function description', type=str, default='')
@click.option('--runtime', '-r', prompt='Your function runtime', type=str, default='python3.6')
def new(name, description, runtime):
    directory = f'functions/{name}'
    os.makedirs(directory)
    test_directory = f'functions/{name}/tests'
    os.makedirs(test_directory)

    ext = _ext(runtime)
    tmpl_env = jinja2.Environment(loader=jinja2.PackageLoader('src', 'templates'))
    main_tmpl = tmpl_env.get_template(f'{runtime}/main.{ext}.tmpl')
    main = main_tmpl.render()
    with open(f'{directory}/main.{ext}', 'w') as f:
        f.write(main)

    func_config_tmpl = tmpl_env.get_template('function.json.tmpl')
    func_config = func_config_tmpl.render({
        'description': description,
        'runtime': runtime,
    })
    with open(f'{directory}/function.json', 'w') as f:
        f.write(func_config)


@apex_cli.group()
def pip():
    pass


@pip.command()
@click.option('--function', '-f', type=str, help='Function name you will use installed package')
@click.option('--name', '-n', type=str, help='Python package name you want to install')
@click.option('--version', '-v', type=str, default='', help='Python package version you want to install')
def install(function, name, version):
    if version:
        version = f'=={version}'

    # piplib.main(['install', '--target', f'functions/{function}', name + version])


if __name__ == '__main__':
    apex_cli()
