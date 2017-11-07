import os
import sys
import shutil
import subprocess
import tempfile
from distutils import sysconfig
from distutils.unixccompiler import UnixCCompiler

CVARS = sysconfig.get_config_vars()

CPP = '''
#include <Python.h>

extern "C" {
	__attribute__((visibility("default"))) unsigned NvOptimusEnablement = 0x00000001;
	__attribute__((visibility("default"))) int AmdPowerXpressRequestHighPerformance = 0x00000001;
}


wchar_t * charToWChar(const char * text) {
    const size_t size = strlen(text) + 1;
    wchar_t * wText = new wchar_t[size];
    mbstowcs(wText, text, size);
    return wText;
}

int main(int argc, char * argv[]) {
	wchar_t ** wargv = new wchar_t * [argc];
	for (int i = 0; i < argc; ++i) {
		wargv[i] = charToWChar(argv[i]);
	}
	Py_Main(argc, wargv);
}
'''

def install():
    unixcc = UnixCCompiler()
    unixcc.add_include_dir(CVARS['INCLUDEPY'])
    unixcc.add_library_dir(os.path.join(CVARS['exec_prefix'], 'libs'))

    with tempfile.TemporaryDirectory() as tempdir:
        cpp = open(os.path.join(tempdir, 'gpython.cpp'), 'w')
        cpp.write(CPP)
        cpp.close()

        args = unixcc.linker_exe
        args += ['-I' + inc for inc in unixcc.include_dirs]
        args += ['gpython.cpp']
        args += ['-L' + inc for inc in unixcc.library_dirs]
        args += [CVARS['BLDLIBRARY'], '-lstdc++']
        args += ['-o', 'gpython']

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=tempdir)
        proc.wait()

        if proc.returncode:
            message = 'compile failed\n\n'
            message += proc.stdout.read().decode()
            raise Exception(message)

        else:
            exe = os.path.join(os.path.dirname(sys.executable), 'gpython')
            shutil.copyfile(os.path.join(tempdir, 'gpython'), exe)
            shutil.copystat(sys.executable, exe)

        proc.stdout.close()


def uninstall():
    exe = os.path.join(os.path.dirname(sys.executable), 'gpython')
    os.unlink(exe)
