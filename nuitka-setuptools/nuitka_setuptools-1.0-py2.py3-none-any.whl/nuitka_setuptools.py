import os
import sys
import shutil
import inspect
import importlib
import subprocess
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext


class NuitkaCompile(Extension):
    def __init__(self, mod, compile_each_file=True, extra_cmd=None, src_age=0):
        """
        Specify the module we want to compile with nuitka
        :param str mod: The import path of the module to compile
        :param bool compile_each_file: True to compile each submodule as separate pyd.
                                       False to compile all into one pyd. Note: this has end use import restrictions
        """
        super(NuitkaCompile, self).__init__(mod, [])
        self.compile_each_file = compile_each_file
        self.extra_cmd = extra_cmd or []
        self.src_age = src_age


def Compile(modules, compile_each_file=True):

    def _find_modules(module_name):
        """ Ideally we want to find all the modules imported by the provided top level module
            The modules that are contained in the top level are returned in submodules
            Other modules that are dependancies should be returned in others.
        """

        _others = set()
        _submodules = set()

        mod = importlib.import_module(module_name)

        if False:
            from modulefinder import ModuleFinder

            finder = ModuleFinder()
            # finder.load_file(mod.__file__)
            pathname = Path(mod.__file__)
            if pathname.name == '__init__.py':
                pathname = pathname.parent
            finder.load_package(module_name, str(pathname))
            modules = set(finder.modules) | set(finder.badmodules)
            modules ^= {'__main__'}

            _others = {name if module_name not in name else name.split('.')[0]
                       for name in finder.modules.keys()}

            _submodules = {name for name in finder.modules.keys() if module_name in name}

        if True:
            def get_imports(_module_name):
                import dis
                mod = importlib.import_module(_module_name)
                instructions = dis.get_instructions(inspect.getsource(mod))
                imports = [i.argval for i in instructions if 'IMPORT' in i.opname]
                subs = [getattr(mod, i, None) or importlib.import_module(i, _module_name) or i for i in imports]

                return subs

            # Just get all submodules from sys.modules
            for key, val in sys.modules.items():
                if module_name in key:
                    _submodules |= {val.__name__}

            for attr, val in mod.__dict__.items():
                # This misses recursive submodules, and ones that are imported like from <module> import <function>
                if inspect.ismodule(val):
                    if module_name in val.__name__:
                        _submodules |= {val.__name__}
                    else:
                        _others |= {val.__name__}

        _submodules ^= {module_name}

        for m in _submodules:
            s, o = _find_modules(m)
            _submodules |= s
            _others |= o
        return _submodules, _others

    extensions = []

    for mod in modules:
        path = mod.split('.')

        submodules, others, = _find_modules(mod)

        extra_cmd = []
        if compile_each_file:
            for sub in {mod} | submodules:
                _mod = importlib.import_module(sub)
                src_age = os.path.getmtime(_mod.__file__)
                extensions.append(NuitkaCompile(sub, compile_each_file, src_age=src_age))

        else:
            head = len('.'.join(path[:-1])) + 1
            submodules = [m[head:] for m in set(submodules)]
            _mod = importlib.import_module(mod)
            _newest = os.path.getmtime(_mod.__file__)
            for sub in submodules:
                _sub = importlib.import_module(sub)
                _newest = os.path.getmtime(_sub.__file__)
                extra_cmd.extend(['--recurse-to', sub])
            for sub in set(others):
                extra_cmd.extend(['--recurse-not-to', sub])

            extensions.append(NuitkaCompile(mod, compile_each_file, extra_cmd=extra_cmd, src_age=_newest))

    return extensions


class Nuitka(build_ext):
    @staticmethod
    def _nuitka_script():
        """
        Only working for windows, find the nuitka run script.
        TODO: setuptools.entry_points handling could probably be used to find the correct location for any platform
        :return:
        """
        path = Path(sys.executable).parent
        if path.name != 'Scripts':
            path = path.join("Scripts")
        if not path.exists():
            raise Exception("Cannot find scripts directory? %s" % path)
        return path / 'nuitka'

    @staticmethod
    def _delete_path(path):
        if Path(path).exists():
            if Path(path).is_dir():
                shutil.rmtree(str(path))
            else:
                os.unlink(str(path))

    @staticmethod
    def cleanup_module(original, cwd, target):
        """ This will delete the original python source and any temp build files
        """
        original = Path(original)
        Nuitka._delete_path(original)
        Nuitka._delete_path(original.with_suffix('.build'))
        Nuitka._delete_path(original.with_suffix('.lib'))
        Nuitka._delete_path(original.with_suffix('.exp'))

        if target == '_init.py':
            with (cwd / '__init__.py').open('w') as stub_init:
                stub_init.write("from ._init import *")

    def run(self):

        for ext in self.extensions:  # type: Compile
            path = ext.name.split('.')
            target = path[-1]
            cwd = Path(os.path.join(self.build_lib, *path[:-1]))

            # mod = importlib.import_module(ext.name)
            original = Path(cwd) / target

            final_pyd_name = Path(getattr(ext, '_file_name')).name

            if ext.compile_each_file:  # is py file
                if original.is_dir():
                    cwd = original
                    init = original / '__init__.py'
                    cname = init.with_name('_init.py')
                    init.rename(cname)
                    original = cname
                    final_pyd_name = '.'.join(('_init', *final_pyd_name.split('.')[1:]))
                else:
                    original = original.with_suffix('.py')
                target = original.name

            final_pyd = cwd / final_pyd_name

            if final_pyd.exists():
                if ext.src_age and os.path.getmtime(str(final_pyd)) > ext.src_age:
                    # No python files have been updated, skip re-compiling
                    self.cleanup_module(original, cwd, target)
                    continue
                else:
                    # Clean up from previous build
                    self._delete_path(final_pyd)

            print("compiling %s -> %s" % ((cwd / target), final_pyd))
            if ext.compile_each_file:
                subprocess.run([sys.executable, str(self._nuitka_script()),
                                '--module', target, '--recurse-none'] + ext.extra_cmd, cwd=str(cwd))
            else:
                subprocess.run([sys.executable, str(self._nuitka_script()), '--module', target,
                                '--recurse-directory', target, '--recurse-to', target] + ext.extra_cmd, cwd=str(cwd))

            pyd = (cwd / target).with_suffix(".pyd")

            if pyd.exists():
                pyd.rename(final_pyd)
                self.cleanup_module(original, cwd, target)
