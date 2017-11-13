from distutils.core import setup
setup(
  name = 'flask_simple_accounts',
  packages = ['flask_simple_accounts'],
  version = '1.11',
  description = 'This library allows Flask developers to use the an api to handle the mundane tasks of user account management',
  author = 'Herbert Dawkins',
  author_email = 'DrDawkins@ClearScienceInc.com',
  url = 'https://github.com/sudouser2010/flask_simple_accounts',
  download_url = 'https://github.com/sudouser2010/flask_simple_accounts/archive/1.0.tar.gz',
  keywords = ['flask', 'simple', 'accounts'],
  classifiers = [],
  python_requires='~=3.6',
  install_requires=[
  'flask_multiple_static_folders', 'flask_beautiful_messages', 'flask_render_specific_template',
  'SQLAlchemy==1.1.10', 'bcrypt==3.1.3', 'Flask-Mail==0.9.1',
  'flask_login'
  ],
)
