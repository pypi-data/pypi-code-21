from flask_script import Manager, prompt
import NodeDefender

manager = Manager(usage='Manage Nodes')

@manager.option('-n', '-name', '--name', dest='name', default=None)
@manager.option('-g', '-group', '--group', dest='group', default=None)
@manager.option('-s', '-street', '--street', dest='street', default=None)
@manager.option('-c', '-city', '--city', dest='city', default=None)
def create(name, group, street, city):
    'Create Node and Assign to Group'
    if name is None:
        name = prompt('Node Name')
    
    if group is None:
        group = prompt('Group Name')
    
    if street is None:
        street = prompt('Street')
    
    if city is None:
        city = prompt('City')
    
    try:
        location = NodeDefender.db.node.location(street, city)
    except LookupError as e:
        print("Error: ", e)
        return

    try:
        NodeDefender.db.node.create(name, group, location)
    except (LookupError, ValueError) as e:
        print("Error: ", e)
        return
        

    print("Node {} Successfully created".format(name))


@manager.option('-n', '--name', dest='name', default=None)
def delete(name):
    'Delete Node'
    if name is None:
        name = prompt('Node Name')
    
    try:
         node.Delete(name)
    except LookupError as e:
        print("Error: ", e)
        return

    print("Node {} Successfully deleted".format(name))

'''
@manager.option('-n', '--name', dest='name', default=None)
@manager.option('-g', '--group', dest='group', default=None)
def join(name, group):
    'Let a Node join a Group'
    if name is None:
        name = prompt("Node Name")

    if group is None:
        group = prompt("Group Name")

    try:
        node.Join(name, group)
    except LookupError as e:
        print("Error: ", e)
        return

    print("Node {}, Successfully joined Group: {}".format(name, group))

@manager.option('-n', '--name', dest='name', default=None)
@manager.option('-group', '--group', dest='group', default=None)
def leave(name, group):
    'Let a Node leave a Group'
    if name is None:
        name = prompt("Node Name")

    if group is None:
        group = prompt("Group Name")
    try:
        node.Leave(name, group)
    except LookupError as e:
        print("Error: ", e)

    print("Node {} Successfully left Group: {}".format(name, group))
'''

@manager.option('-n', '--name', dest='name', default=None)
def get(name):
    'Get a specific Node'
    if name is None:
        name = prompt("Node Name")
    
    n = node.Get(name)
    if n is None:
        print("Unable to find Node")
        return
    
    print("ID: {}, Name: {}".format(n.id, n.name))
    print("Location: {}, {}".format(n.location.street, n.location.city))
    print("Lat: {}, Long: {}".format(n.location.longitude,
                                     n.location.latitude))
    print("Group: ", n.group.name)
    if n.icpe:
        print("iCPE: ", n.icpe.name)

@manager.command
def list():
    'List avalible Nodes'
    for n in node.List():
        print("ID: {}, Alias: {}".format(n.id, n.name))

'''
@manager.option('-name', '--name', dest='name', default=None)
def groups(name):
    'Get Groups that a Node belongs to'
    if name is None:
        name = prompt("Node Name")

    for n in node.Groups(name):
        print("ID: {}, Name: {}".format(n.id, n.name))


@manager.option('-name', '--name', dest='name', default=None)
def icpes(name):
    'Get iCPEs that belong to Node'
    if name is None:
        name = prompt("Node Name")

    for n in node.iCPEs(name):
        print("ID: {}, Name: {}".format(n.id, n.name))
'''
