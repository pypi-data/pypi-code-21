# coding=utf-8

"""
This file contains legacy functions used for DB migration to amazon, in the original initial_deploy fabric file.
We preserve this because we may use some of this code in the future.
"""

from fabric.decorators import task
from fabric.operations import local, run, os
from fabric.state import env


@task
def copy_data_from_old_db_to_new_db():
    copy_backup_to_new_db()


@task
def make_backup_data_from_old_db():
    remote_back_up_path = env.conf.get('REMOTE_OLD_DB_BACKUP_DIR_PATH')
    backup_file_path = os.path.join(remote_back_up_path,
                                    env.conf.get('BACKUP_FILENAME'))
    print("Performing remote DB backup...")
    run('mkdir -p %s' % remote_back_up_path)
    if env.conf.get('REMOTE_DB_BACKEND') == 'mysql':
        run("mysqldump -u %(db_user)s -p%(db_pass)s -h %(host)s %(db)s -f %(backup_file_path)s" %
            {'db_user': env.conf.get('REMOTE_OLD_DB_USER'),
             'db_p'
             'ass': env.conf.get('REMOTE__OLD_DB_PASSWORD'),
             'db': env.conf.get('REMOTE_OLD_DB_NAME'),
             'backup_file_path': backup_file_path,
             'host': env.conf.get('REMOTE_OLD_DB_HOST'),
             })
    elif env.conf.get('REMOTE_DB_BACKEND') == 'postgresql':
        run('PGPASSWORD="%(db_pass)s" pg_dump -h %(host)s -U %(db_user)s %(db)s -f %(backup_file_path)s' %
            {'db_user': env.conf.get('REMOTE_OLD_DB_USER'),
             'db_pass': env.conf.get('REMOTE__OLD_DB_PASSWORD'),
             'db': env.conf.get('REMOTE_OLD_DB_NAME'),
             'backup_file_path': backup_file_path,
             'host': env.conf.get('REMOTE_OLD_DB_HOST'),
             })


@task
def copy_backup_to_new_db():
    create_back_up_path()
    remote_backup_file_path = os.path.join(env.conf.get('REMOTE_DB_BACKUP_DIR_PATH'),
                                           env.conf.get('BACKUP_FILENAME'))

    local('scp -i %(keyfile)s %(backup_local_path)s %(remote_user)s@%(remote_host)s:%(backup_file_path)s' %
          {'remote_user': env.user,
           'remote_host': env.hosts[0],
           'keyfile': env.key_filename,
           'backup_file_path': remote_backup_file_path,
           'backup_local_path': env.conf.get('BACKUP_LOCAL_PATH')})

    populate_remote_db(db_user=env.conf.get('REMOTE_DB_USER'),
                       backup_file_path=remote_backup_file_path,
                       db_name=env.conf.get('REMOTE_DB_NAME'),
                       db_password=env.conf.get('REMOTE_DB_PASSWORD'),
                       db_host=env.conf.get('REMOTE_DB_HOST'))


def create_back_up_path():
    remote_backup_file_path = env.conf.get('REMOTE_DB_BACKUP_DIR_PATH')

    run('mkdir -p %s' % remote_backup_file_path)


@task
def populate_remote_db(db_user, db_password, db_name, db_host, backup_file_path):
    if env.conf.get('REMOTE_DB_BACKEND') == 'mysql':
        command = 'mysql -u %(db_user)s -p%(db_pass)s -h %(host)s -d %(db)s -f %(backup_file_path)s'
    elif env.conf.get('REMOTE_DB_BACKEND') == 'postgresql':
        command = 'PGPASSWORD="%(db_pass)s" psql -U %(db_user)s -h %(host)s  -d %(db)s -f  %(backup_file_path)s'
    else:
        raise NotImplementedError("Unsupported DB!")

    run(command % {'db_user': db_user, 'db_pass': db_password, 'db': db_name, 'backup_file_path': backup_file_path,
                   'host': db_host})
