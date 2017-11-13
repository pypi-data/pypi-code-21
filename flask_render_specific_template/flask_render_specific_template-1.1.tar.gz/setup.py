from distutils.core import setup
setup(
  name = 'flask_render_specific_template',
  packages = ['flask_render_specific_template'],
  version = '1.1',
  description = 'This library allows Flask developers to dynamically select the template directory used for rendering',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  url = 'https://github.com/sudouser2010/flask_render_specific_template',
  download_url = 'https://github.com/sudouser2010/flask_render_specific_template/archive/1.0.tar.gz',
  keywords = ['flask', 'dynamic', 'specific', 'template'],
  classifiers = [],
  install_requires=[
  'flask==0.12.2',
  ],
)
