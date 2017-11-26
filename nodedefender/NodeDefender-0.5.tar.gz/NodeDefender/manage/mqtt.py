from flask_script import Manager, prompt
import NodeDefender

manager = Manager(usage='Manage MQTT')

@manager.option('-h', '-host', '--host', dest='host', default=None)
@manager.option('-p', '-port', '--port', dest='port', default=None)
@manager.option('-u', '-username', '--username', dest='username', default=None)
@manager.option('-pw', '--password', dest='password', default=None)
def create(host, port, username, password):
    'Create Node and Assign to Group'
    if host is None:
        host = prompt('Host Address')
    
    if port is None:
        port = prompt('Port Number')
    
    '''
    if username is None:
        username = prompt('Username(blank for None)')
        if not len(username):
            username = None
    
    if password is None:
        password = prompt('Password(blank for None)')
        if not len(password):
            password = None
    '''

    try:
        NodeDefender.db.mqtt.create(host, port)
    except ValueError as e:
        print("Error: ", e)
        return

    print("MQTT {}:{} Successfully created".format(host, port))


@manager.option('-i', '--host', dest='host', default=None)
def delete(host):
    'Delete Node'
    if host is None:
        host = prompt('Host Address')
    
    try:
         NodeDefender.db.mqtt.delete(host)
    except LookupError as e:
        print("Error: ", e)
        return

    print("MQTT {} Successfully deleted".format(host))

@manager.command
def list():
    for mqtt in NodeDefender.db.mqtt.list():
        print("ID: {}, IP: {}:{}".format(mqtt.id, mqtt.host, mqtt.port))

