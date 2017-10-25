from djangoforandroid.core.toolchain import PythonRecipe
import os
import shutil

class DjangoforandroidRecipe(PythonRecipe):

    version = 'tip'
    #url = 'https://bitbucket.org/yeisoneng/django-for-android/get/{version}.tar.gz'
    url = 'https://bitbucket.org/djangoforandroid/django-for-android/get/{version}.tar.gz'
    depends = ['python3crystax']


    def build_arch(self, arch):
        '''Install the Python module by calling setup.py install with
        the target Python dir.'''
        super(DjangoforandroidRecipe, self).build_arch(arch)

        #shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'djangoforandroid', 'app'))
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'djangoforandroid', 'builder'))
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'djangoforandroid', 'core'))
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'djangoforandroid', 'recipes'))
        shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'djangoforandroid', 'src'))
        #shutil.rmtree(os.path.join(self.get_build_dir(arch.arch), 'djangoforandroid', 'views'))

        self.install_python_package(arch)
        #source, cwd


recipe = DjangoforandroidRecipe()