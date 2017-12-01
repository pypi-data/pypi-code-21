import click


def _validate_name(context, params, value):
    if not value:
        raise click.BadParameter('Function name must not be emtpy')

    directory = f'functions/{value}'
    if os.path.exists(directory):
        raise click.BadParameter(f'The function name {value} already exists')

    return value


def _validate_runtime(context, params, value):
    available_runtime = ['python3.6']
    if value not in available_runtime:
        runtimes = ', '.join(available_runtime)
        raise click.BadParameter(f'{value} is a wrong runtime. Available runtimes are {runtimes}')
    return value


def _extension(runtime):
    return {
        'python3.6': 'py',
    }[runtime]


@click.command()
@click.option('--name', '-n', prompt='Your function name', type=str, callback=_validate_name)
@click.option('--description', '-d', prompt='Your function description', type=str, default='')
@click.option('--runtime', '-r', prompt='Your function runtime', type=str, default='python3.6', callback=_validate_runtime)
def function(name, description, runtime):
    directory = f'functions/{name}'
    os.makedirs(directory)

    func_config_tmpl = tmpl_env.get_template('function.json.tmpl')
    func_config = func_config_tmpl.render({
        'description': description,
        'runtime': runtime,
    })
    with open(f'{directory}/function.json', 'w') as f:
        f.write(func_config)

    ext = _extension(runtime)
    tmpl_env = jinja2.Environment(loader=jinja2.PackageLoader('src', 'templates'))
    main_tmpl = tmpl_env.get_template(f'{runtime}/main.{ext}.tmpl')
    main = main_tmpl.render()
    with open(f'{directory}/main.{ext}', 'w') as f:
        f.write(main)

    test_directory = f'functions/{name}/tests'
    os.makedirs(test_directory)
    if runtime == 'python3.6':
        test_tmpl = tmpl_env.get_template(f'{runtime}/tests/test_test.py.tmpl')
        with open(f'{test_directory}/test_test.{ext}', 'w') as f:
            f.write(func_config)
