import argparse
import ast
import csv
import importlib.machinery
import json
import os.path
from pathlib import Path
import re
from stdlib_list import stdlib_list
import subprocess
import sys
from tempfile import TemporaryDirectory

launcher_tpl_file = Path(__file__).parent / 'launcher.py'

def modules_from_dist_info(d: Path):
    with (d / 'RECORD').open('r') as f:
        files = [row[0] for row in csv.reader(f)]

    res = set()
    for path in files:
        if '__pycache__' in path:
            continue
        if os.path.isabs(path):
            path = os.path.normpath(path)
            if path.startswith(str(d.parent)):
                # Relative path from site-packages
                path = path[len(str(d.parent)):].replace(os.sep, '/')
            else:
                continue

        for suffix in importlib.machinery.all_suffixes():
            if path.endswith(suffix):
                module = path[:-len(suffix)].replace('/', '.')
                if module.endswith('.__init__'):
                    module = module[:-9]
                res.add(module)
                break

    return res

def files_from_dist_info(d: Path):
    with (d / 'RECORD').open('r') as f:
        files = [row[0] for row in csv.reader(f)]

    res = set()
    for path in files:
        if '__pycache__' in path:
            continue
        if not os.path.isabs(path):
            path = str(d.parent / path)
        res.add(path)

    return res

def find_distributions():
    files_to_distribs = {}

    for packagedir in sys.path:
        packagedir = Path(packagedir)
        if not packagedir.is_dir():
            continue
        for path in packagedir.iterdir():
            m = re.match(r'^(.*)-(.*)\.dist-info$', path.name)
            if m and path.is_dir():
                for filepath in files_from_dist_info(path):
                    files_to_distribs[filepath] = m.group(1, 2)

    return files_to_distribs

def classify(modules: dict):
    remainder = modules.copy()
    res = {'distributions': {}, 'stdlib': [], 'unknown': {}, 'notfiles': []}

    # Identify stdlib modules
    for modname in stdlib_list():
        if modname in remainder:
            res['stdlib'].append(modname)
            del remainder[modname]

    files_to_distribs = find_distributions()

    for modname, filepath in sorted(remainder.items()):
        if filepath is None:
            res['notfiles'].append(modname)
        elif filepath in files_to_distribs:
            distname, version = files_to_distribs[filepath]
            if distname in res['distributions']:
                res['distributions'][distname]['modules_loaded'].append(modname)
            else:
                res['distributions'][distname] = {
                    'modules_loaded': [modname],
                    'version': version
                }
        else:
            res['unknown'][modname] = filepath

    return res

def summarise_classified(classified):
    n_from_dist = sum(len(d['modules_loaded'])
                     for d in classified['distributions'].values())
    n_stdlib = len(classified['stdlib'])
    n_notfiles = len(classified['notfiles'])
    n_unknown = len(classified['unknown'])

    print()
    print("Kartoffel identified {} modules:".format(
        n_from_dist + n_stdlib + n_notfiles + n_unknown))
    print('{} from {} distributions'.format(
            n_from_dist, len(classified['distributions'])))
    for dname, dinfo in classified['distributions'].items():
        print('  {}=={}'.format(dname, dinfo['version']))

    print('{} from standard library'.format(n_stdlib))
    print('{} built-in or dynamically created modules'.format(n_notfiles))
    print('{} unidentified'.format(n_unknown))

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('entrypoint')
    ap.add_argument('args', nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    
    module, func = args.entrypoint.split(':')
    with TemporaryDirectory() as td:
        output_file = Path(td, 'modules_loaded')
        launch_file = Path(td, 'launch.py')
        launcher_script = (launcher_tpl_file.read_text('utf-8')
                            .replace('_module_', module)
                            .replace('_func_', func)
                            .replace('_output_file_', repr(str(output_file)))
                           )
        launch_file.write_text(launcher_script, 'utf-8')
        subprocess.run([sys.executable, str(launch_file)] + args.args)
        modules_loaded = ast.literal_eval(output_file.read_text('utf-8'))
    
    classified = classify(modules_loaded)
    summarise_classified(classified)
    with open('kartoffel-result.json', 'w', encoding='utf-8') as f:
        json.dump(classified, f, indent=2, sort_keys=True)
    print("Data written to 'kartoffel-result.json'")
    
if __name__ == '__main__':
    main()
