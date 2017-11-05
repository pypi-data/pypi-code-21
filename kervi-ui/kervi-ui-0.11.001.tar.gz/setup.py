from distutils.core import setup
import distutils
from kervi_ui.version import VERSION

try:
    distutils.dir_util.remove_tree("dist")
except:
    pass

setup(
    name='kervi-ui',
    packages=['kervi_ui'],
    version=VERSION,
    description='UI module for the kervi framework. It is included as dependency when kervi in installed.',
    author='Tim Wentzlau',
    author_email='tim.wentzlau@gmail.com',
    url='https://github.com/kervi/kervi-ui',
    download_url='https://github.com/wentzlau/kervi-ui/archive/v1.0-alpha.tar.gz',
    keywords=['ui', 'robotic', 'automation'],
    classifiers=[],
    package_data={
        'kervi_ui': [
            'web/dist/*.html',
            'web/dist/*.js',
            'web/dist/*.css',
            'web/dist/*.map',
            'web/dist/*.ico',
            'web/dist/*.png',
            'web/dist/*.eot',
            'web/dist/*.svg',
            'web/dist/*.woff',
            'web/dist/*.woff2',
            'web/dist/*.ttf'
            ],
    },
)

