import os
from setuptools import setup
from setuptools.extension import Extension
from distutils.command.build import build
from distutils.command.build_ext import build_ext

custom_cmd_class = {}

class CustomBuild(build):
    sub_commands = [
        ('build_ext', build.has_ext_modules),
        ('build_py', build.has_pure_modules),
        ('build_clib', build.has_c_libraries),
        ('build_scripts', build.has_scripts),
    ]

custom_cmd_class['build'] = CustomBuild

try:
    from wheel.bdist_wheel import bdist_wheel

    class CustomBdistWheel(bdist_wheel):
        def run(self):
            self.run_command('build_ext')
            bdist_wheel.run(self)

    custom_cmd_class['bdist_wheel'] = CustomBdistWheel
except ImportError:
    pass  # custom command not needed if wheel is not installed

class CustomBuildExt(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())
        self.swig_opts.extend(["-c++"] + ["-I" + d for d in self.include_dirs])

custom_cmd_class['build_ext'] = CustomBuildExt

build_requires= []

try:
    import numpy
except ImportError:
    build_requires = ['numpy>=1.9.0']

hgversion = 'unknown'

clstm = Extension('_clstm',
        libraries = ['png','protobuf'],
        include_dirs = ['/usr/include/eigen3', '/usr/local/include/eigen3', '/usr/local/include', '/usr/include/hdf5/serial'],
        extra_compile_args = ['-std=c++11','-w',
            '-Dadd_raw=add','-DNODISPLAY=1','-DTHROW=throw',
            '-DHGVERSION="\\"'+hgversion+'\\""'],
        sources=['clstm.i','clstm.cc','clstm_prefab.cc','extras.cc',
                 'ctc.cc','clstm_proto.cc','clstm.pb.cc'])

print("making proto file")
os.system("protoc clstm.proto --cpp_out=.")

setup(
    name='clstm',
    version='0.0.5',
    cmdclass=custom_cmd_class,
    author='Thomas Breuel',
    description='clstm - swig python bindings for the clstm library',
    license='Apache 2.0',
    url='https://github.com/tmbdev/clstm',
    long_description='',
    classifiers=[
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    py_modules = ["clstm"],
    ext_modules = [clstm],
    setup_requires = build_requires,
    install_requires = ['numpy>=1.9.0'],
)
