from flask_script import Manager, Command, prompt, prompt_pass
import NodeDefender

manager = Manager(usage="Preform User- operations in SQL Database")

@manager.option('-n', '-e', '--email', dest='email', default=None)
@manager.option('-pw', '--password', dest='password', default=None)
def create(email, password):
    'Create User Account'
    if email is None:
        email = prompt('Email')

    if password is None:
        password = prompt_pass('Password')
    
    try:
        NodeDefender.db.user.create(email)
        NodeDefender.db.user.set_password(email, password)
        NodeDefender.db.user.enable(email)
    except ValueError:
        print("User already present")
        return

    print("User {} Successfully added!".format(email))


@manager.option('-n', '-e', '--email', dest='email', default=None)
def delete(email):
    "Deltes User"
    if email is None:
        email = prompt('Email')

    try:
        u = NodeDefender.db.user.delete(email)
    except LookupError as e:
        print("Error: ", e)

    print("User {} Successfully Deleted!".format(u.email))

@manager.option('-n', '-e', '--email', dest='email', default=None)
def enable(email):
    "Enable User"
    if email is None:
        email = prompt('Email')

    try:
        user = NodeDefender.db.user.enable(email)
    except LookupError as e:
        print("Error: ", e)

    print("User {} Successfully Enabled!".format(user.email))

@manager.option('-n', '-e', '--email', dest='email', default=None)
def disable(email):
    "Disable User"
    if email is None:
        email = prompt('Email')

    try:
        user = NodeDefender.db.user.disable(email)
    except LookupError as e:
        print("Error: ", e)

    print("User {} Successfully Locked!".format(user.email))

@manager.command
def list():
    "List Users"
    for user in NodeDefender.db.user.list():
        print("ID: {}, Email: {}".format(user.id, user.email))

@manager.option('-n', '-e', '--email', dest='email', default=None)
def groups(email):
    "List User Groups"
    if email is None:
        email = prompt('Email')
    for group in NodeDefender.db.user.groups(email):
        print("ID: {}, Name: {}".format(group.id, group.name))

@manager.option('-n', '-e', '--email', dest='email', default=None)
@manager.option('-g', '--group', dest='group', default=None)
def join(email, group):
    'Add Group to User'
    if email is None:
        email = prompt('Email')
    if group is None:
        group = prompt('Group')

    try:
        NodeDefender.db.group.add_user(group, email)
    except LookupError as e:
        print("Error: ", e)
        return

    print("User {}, Successfully added to {}".format(email, group))

@manager.option('-n', '-e', '--email', dest='email', default=None)
@manager.option('-g', '--group', dest='group', default=None)
def leave(email, group):
    'Remove Role from User'
    if email is None:
        email = prompt('Email')
    if group is None:
        group = prompt('Group')
        
    try:
        NodeDefender.db.group.remove_user(group, email)
    except LookupError as e:
        print("Error: ", e)
        return

    print("User {}, Successfully removed from {}".format(email, group))
