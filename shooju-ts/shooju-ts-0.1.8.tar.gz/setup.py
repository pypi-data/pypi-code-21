try:
    from setuptools import setup, Extension, Command
    from setuptools.command import sdist as _sdist, install as _install
except ImportError:
    from distutils.core import setup, Extension, Command
    from distutils.command import sdist as _sdist, install as _install
try:
    from wheel import bdist_wheel as _bdist_wheel
except ImportError:
    _bdist_wheel = None

import re
import os
from contextlib import contextmanager

import shutil
import numpy as np

SJTS_PATH = './sjts'


@contextmanager
def sjts_source(sjts_path):
    assert os.path.exists(sjts_path), 'sjts source is not found at {}.' \
                                      ' specify path to sjts source with "sjts-path" parameter'.format(sjts_path)
    do_clean_up = False
    if sjts_path != SJTS_PATH:
        try:
            shutil.copytree(sjts_path, SJTS_PATH)
            do_clean_up = True
        except (IOError, OSError):
            pass

    if do_clean_up:
        try:
            shutil.rmtree('./sjts/.git')  # todo why this is necessary?
        except (IOError, OSError):
            pass
    try:
        yield
    except Exception:
        raise
    finally:
        if do_clean_up:
            shutil.rmtree('./sjts')


def prepare_cmd_class(base_class):
    class Cmd(base_class):
        user_options = base_class.user_options \
                       + [('sjts-path=', 'd', "sjts sources path" "[default: {}]".format(SJTS_PATH)), ]

        def initialize_options(self, *args, **kwargs):
            self.sjts_path = SJTS_PATH
            base_class.initialize_options(self, *args, **kwargs)

        def run(self, *args, **kwargs):
            with sjts_source(self.sjts_path):
                base_class.run(self, *args, **kwargs)

    return Cmd


extmod = Extension('sjts',
                   sources=['./python/ujson.c',
                            './python/objToJSON.c',
                            './python/JSONtoObj.c',
                            './sjts/sjtsdec.c',
                            './sjts/sjtsenc.c',
                            './sjts/ultrajsonenc.c',
                            './sjts/ultrajsondec.c'],
                   include_dirs=[np.get_include(), './python', './lib', SJTS_PATH],
                   extra_compile_args=['-D_GNU_SOURCE'])


def get_version():
    filename = os.path.join(os.path.dirname(__file__), './python/version.h')
    file = None
    try:
        file = open(filename)
        header = file.read()
    finally:
        if file:
            file.close()
    m = re.search(r'#define\s+UJSON_VERSION\s+"(\d+\.\d+(?:\.\d+)?)"', header)
    assert m, "version.h must contain UJSON_VERSION macro"
    return m.group(1)


f = open('README.rst')
try:
    README = f.read()
finally:
    f.close()

cmd_classes = {
    'sdist': prepare_cmd_class(_sdist.sdist),
    'install': prepare_cmd_class(_install.install)
}
if _bdist_wheel is not None:
    cmd_classes['bdist_wheel'] = prepare_cmd_class(_bdist_wheel.bdist_wheel)

setup(name='shooju-ts',
      version=get_version(),
      description="Shooju Time Series (SJTS) Serializer",
      long_description=README,
      ext_modules=[extmod],
      cmdclass=cmd_classes,
      keywords='data, client, shooju',
      author='Shooju, LLC',
      author_email='support@shooju.com',
      url='http://shooju.com',
      license='TBD',
      platforms=['any'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[]
      )
