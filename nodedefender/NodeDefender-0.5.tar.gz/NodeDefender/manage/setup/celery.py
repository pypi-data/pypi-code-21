from NodeDefender.manage.setup import (manager, print_message, print_topic,
                                       print_info)
from flask_script import prompt
import NodeDefender


supported_brokers = ['amqp', 'redis']

@manager.command
def celery():
    print_topic("Celery")
    print_info("Celery is used for concurrent operation. It will spawn multiple\
               workes on multiple CPU cores and possibly even on multiple\
               hosts, running as a cluster. Disabling Celery will make\
               NodeDefender as a single process. Celery requires AMQP or Redis\
               to communicate between workes")
    enabled = None
    while enabled is None:
        enabled = prompt("Enable Celery(Y/N)").upper()
        if 'Y' in enabled:
            enabled = True
        elif 'N' in enabled:
            enabled = False
        else:
            enabled = None
    NodeDefender.config.celery.set_cfg(enabled = enabled)
    if not enabled:
        return True
    
    broker = None
    while broker is None:
        broker = prompt("Enter Broker type(AMQP or Redis)").lower()
        if broker not in supported_brokers:
            broker = None
    NodeDefender.config.celery.set_cfg(broker = broker)

    server = None
    while server is None:
        server = prompt("Enter Server Address")
    NodeDefender.config.celery.set_cfg(server = server)

    port = None
    while port is None:
        port = prompt("Enter Server Port")
    NodeDefender.config.celery.set_cfg(port = port)

    database = ''
    while not database:
        database = prompt("Enter Database")
    NodeDefender.config.celery.set_cfg(database = database)
    return True
