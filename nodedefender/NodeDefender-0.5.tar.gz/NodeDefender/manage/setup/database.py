from NodeDefender.manage.setup import (manager, print_message, print_topic,
                                       print_info)
from flask_script import prompt
import NodeDefender

@manager.command
def database():
    print_topic('Database')
    print_info("Database is used to store presistant data.")
    print_info("By having it disabled the data will be store in run-time RAM for the\
               session")
    enabled = None
    while enabled is None:
        enabled = prompt("Enable Database(Y/N)").upper()
        if 'Y' in enabled:
            enabled = True
        elif 'N' in enabled:
            enabled = False
        else:
            enabled = None
    
    NodeDefender.config.database.set_cfg(enabled = enabled)
    if enabled:
        config_database_engine()
    return True

def config_database_engine():
    supported_databases = ['mysql', 'sqlite']
    engine = None
    while engine is None:
        engine = prompt("Enter DB Engine(SQLITE, MySQL)").lower()
        if engine not in supported_databases:
            engine = None

    NodeDefender.config.database.set_cfg(engine = engine)
    if engine == 'mysql':
        config_database_host()
        config_database_user()
    
    if engine == 'sqlite':
        config_database_file()
    return True

def config_database_host():
    server = None
    while not server:
        server = prompt('Enter Server Address')

    port = None
    while not port:
        port = prompt('Enter Server Port')
    
    NodeDefender.config.database.set_cfg(server = server,\
                                         port = port)
    return True

def config_database_user():
    username = None
    while not username:
        username = prompt('Enter Username')

    password = None
    while not password:
        password = prompt('Enter Password')

    db = None
    while not db:
        db = prompt("Enter DB Name/Number")

    NodeDefender.config.database.set_cfg(username = username,\
                                         password = password,\
                                         db = db)
    return True

def config_database_file():
    filepath = None
    while not filepath:
        print("FilePath for SQLite Database, Enter leading slash(/) for\
              absolute- path. Otherwise relative to your current folder.")
        filepath = prompt("Enter File Path")
    
    if filepath[0] == '/':
        filepath = filepath
    else:
        filepath = NodeDefender.config.basepath + '/' + filepath

    NodeDefender.config.database.set_cfg(filepath = filepath)
    return True


