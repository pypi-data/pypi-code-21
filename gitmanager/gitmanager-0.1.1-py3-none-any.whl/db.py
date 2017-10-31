import os

db_directory = '{home}/.gitmanager'.format(home=os.path.expanduser('~'))
db_path = os.path.join(db_directory, 'gitmanager.db')
db_connect = 'sqlite:////{path}'.format(path=db_path)
