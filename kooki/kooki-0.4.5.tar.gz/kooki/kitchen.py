import os, yaml, em, importlib, tempfile, sys

from . import DocumentException
from .tools.output import Output
from .tools import read_file, write_file, DictAsMember
from .config import get_kooki_dir

class Kitchen():

    def __init__(self):

        self._config = DictAsMember()

    def cook(self, name, document):

        try:
            Output.start_step('jars')
            self._config['jars'] = check_jars(document)

            recipe_counter = 1
            recipes_len = len(document.recipe)

            for recipe_module in document.recipe:

                Output.title('{0} ({1}/{2})'.format(name, recipe_counter, recipes_len))

                Output.start_step('recipe')
                infos = []

                self._config['temp_dir'] = tempfile.mkdtemp()
                found_recipe = False

                try:
                    module = importlib.import_module(recipe_module)
                    infos.append({'name': recipe_module, 'status': '[found]'})
                    Output.infos(infos, [('name', 'blue'), ('status', 'green')])
                    found_recipe = True
                except ImportError as e:
                    infos.append({'name': recipe_module, 'status': ('[missing]', 'red')})
                    Output.infos(infos, [('name', 'blue'), ('status', 'green')])
                    raise(e)

                if found_recipe:
                    recipe = getattr(module, 'recipe')
                    recipe(document, self._config)

                if Output.debug:
                    Output.info('Temporary files: {0}'.format(self._config.temp_dir))

                recipe_counter += 1

            if not document.recipe:
                Output.title(name)
                Output.start_step('recipe')
                Output.error('no recipe provided for this target')

        except AttributeError as e:
            Output.error_step('errors')
            Output.error(e)
            sys.exit()

        except ImportError as e:
            Output.error_step('errors')
            Output.error(e)
            sys.exit()

        except DocumentException as e:
            Output.error_step('errors')
            Output.error(e)
            sys.exit()

def check_jars(document):

    infos = []
    error = False
    jars = []

    resources_dir = get_kooki_dir()
    user_jars_dir = os.path.join(resources_dir, 'jars')

    if len(document.jars) > 0:

        for package in document.jars:

            package_path = os.path.join(user_jars_dir, package)

            if os.path.isdir(package_path):
                infos.append({'name': package, 'status': '[found]', 'path': package_path})
                jars.append(package_path)
            else:
                infos.append({'name': package, 'status': ('[missing]', 'red'), 'path': ''})
                error = True

        Output.infos(infos, [('name', 'blue'), ('status', 'green'), ('path', 'cyan')])

        if error: raise DocumentException('Missing jars')

    else:
        Output.info('No jars')

    return jars

import argparse
from vcstool.commands.export import ExportCommand
from vcstool.crawler import find_repositories
from vcstool.executor import ansi, execute_jobs, generate_jobs, output_repositories, output_results


def freeze_kooki(version):
    Output.start_step('kooki')
    Output._print_colored('version ', 'blue', end='')
    Output._print_colored(version, 'cyan')
    return version


def freeze_jars(document):

    infos = []
    jars = {}

    resources_dir = get_kooki_dir()
    user_jars_dir = os.path.join(resources_dir, 'jars')

    Output.start_step('jars')

    if len(document.jars) > 0:

        for jar in document.jars:

            jar_path = os.path.join(user_jars_dir, jar)

            Output._print_colored(jar, 'blue')
            Output._print_colored('  path: ', 'yellow', end='')

            if os.path.isdir(jar_path):
                export_args = argparse.Namespace()
                export_args.path = jar_path
                export_args.exact = True
                command = ExportCommand(export_args)
                clients = find_repositories([jar_path])
                jobs = generate_jobs(clients, command)
                results = execute_jobs(jobs)

                Output._print_colored(jar_path, 'cyan')
                Output._print_colored('  vcs: ', 'yellow', end='')

                if results == []:
                    Output._print_colored('[missing]', 'red')
                elif len(results) == 1:
                    result = results[0]
                    export_data = result['export_data']
                    vcs_type = result['client'].__class__.type
                    vcs_url = export_data['url']
                    vcs_version = export_data['version']

                    Output._print_colored(vcs_type, 'cyan')
                    Output._print_colored('  url: ', 'yellow', end='')
                    Output._print_colored(vcs_url, 'cyan')
                    Output._print_colored('  version: ', 'yellow', end='')
                    Output._print_colored(vcs_version, 'cyan')

                    save_jar = {}
                    save_jar['type'] = vcs_type
                    save_jar['url'] = vcs_url
                    save_jar['version'] = vcs_version
                    jars[jar] = save_jar

            else:
                Output._print_colored('[missing]', 'red')

    else:
        Output.info('No jars')

    return jars


def check_kooki_freeze(version, freeze_data):

    # check kooki version
    Output.start_step('kooki')
    if freeze_data['kooki'] != version:
        Output._print_colored('version needed ', 'blue', end='')
        Output._print_colored(freeze_data['kooki'], 'cyan', end='')
        Output._print_colored(', version installed ', 'blue', end='')
        Output._print_colored(version, 'cyan', end='')
        Output._print_colored(' [bad kooki version]', 'red')
    else:
        Output._print_colored('version ', 'blue', end='')
        Output._print_colored(version, 'cyan', end='')
        Output._print_colored(' [good kooki version]', 'green')

    jars = get_jars()

    Output.start_step('jars')
    for jar in freeze_data['repositories']:
        version_freezed = freeze_data['repositories'][jar]['version']
        Output._print_colored(jar, 'blue')
        Output._print_colored('  freezed: ', 'yellow', end='')
        Output._print_colored(version_freezed, 'cyan')
        Output._print_colored('  installed: ', 'yellow', end='')
        if jar in jars:
            version_installed = jars[jar]['version']
            if version_freezed == version_installed:
                Output._print_colored(version_installed, 'green')
            else:
                Output._print_colored(version_installed, 'red', end='')
                Output._print_colored(' [bad version installed]', 'red')
        else:
            Output._print_colored('[jar not installed]', 'red')


from vcstool.commands.import_ import ImportCommand
from vcstool.commands.import_ import generate_jobs as import_generate_jobs
from vcstool.commands.import_ import add_dependencies as import_add_dependencies
from vcstool.commands.import_ import get_repositories as import_get_repositories


def apply_kooki_freeze(freeze_data, freeze_file):
    jars = get_jars()
    Output.start_step('jars')
    for jar in freeze_data['repositories']:
        version_freezed = freeze_data['repositories'][jar]['version']
        Output._print_colored(jar, 'blue')
        Output._print_colored('  freezed: ', 'yellow', end='')
        Output._print_colored(version_freezed, 'cyan')
        Output._print_colored('  installed: ', 'yellow', end='')
        if jar in jars:
            version_installed = jars[jar]['version']
            if version_freezed == version_installed:
                Output._print_colored(version_installed, 'green')
            else:
                Output._print_colored('Installing new version')
                apply_vcs_import(freeze_file)
        else:
            Output._print_colored('Installing new jar')
            apply_vcs_import(freeze_file)


def apply_vcs_import(freeze_file):
    resources_dir = get_kooki_dir()
    user_jars_dir = os.path.join(resources_dir, 'jars')
    repos = import_get_repositories(freeze_file)
    import_args = argparse.Namespace()
    import_args.path = user_jars_dir
    import_args.force = False

    jobs = import_generate_jobs(repos, import_args)
    import_add_dependencies(jobs)

    results = execute_jobs(jobs, show_progress=True, number_of_workers=1, debug_jobs=False)
    output_results(results)


def get_jars():
    resources_dir = get_kooki_dir()
    user_jars_dir = os.path.join(resources_dir, 'jars')

    jars = {}

    for jar in os.listdir(user_jars_dir):
        jar_path = os.path.join(user_jars_dir, jar)
        export_args = argparse.Namespace()
        export_args.path = jar_path
        export_args.exact = True
        command = ExportCommand(export_args)
        clients = find_repositories([jar_path])
        jobs = generate_jobs(clients, command)
        results = execute_jobs(jobs)

        if len(results) == 1:
            result = results[0]
            if 'export_data' in result:
                export_data = result['export_data']
                vcs_type = result['client'].__class__.type
                vcs_url = export_data['url']
                vcs_version = export_data['version']
                save_jar = {}
                save_jar['type'] = vcs_type
                save_jar['url'] = vcs_url
                save_jar['version'] = vcs_version
                jars[jar] = save_jar

    return jars
