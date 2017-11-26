from NodeDefender.manage.setup import (manager, print_message, print_topic,
                                       print_info)
from flask_script import prompt
import NodeDefender


@manager.command
def general():
    print_topic("General configuration")
    print_info("Server Name. If you are using a local running server please enter\
          as format NAME:PORT. Otherwise it will be\
          generating non- accessable URLs")
    print("/ Example: 127.0.0.1:5000")
    servername = None
    while servername is None:
        servername = prompt("Enter Server Name")
    NodeDefender.config.general.set_cfg(servername = servername)

    port = None
    while port is None:
        port = prompt("Which port should the server be running on")
    NodeDefender.config.general.set_cfg(port = port)

    print_info("Security Key is used to Encrypt Password etc.")
    key = None
    while key is None:
        key = prompt("Enter Secret Key")
    NodeDefender.config.general.set_cfg(secret_key = key)

    print_info("Salt is used to genereate URLS and more.")
    salt = None
    while salt is None:
        salt = prompt("Please enter Salt")
    NodeDefender.config.general.set_cfg(salt = salt)
    
    print_info("You can either have users register by themselfs on the\
               authentication- page or via invite mail. Invite mail requires\
               that you also enable mail- support so that NodeDefender can send\
               invitation- mail and such. Superuser can still administrate\
               users in the same way.")
    self_registration = None
    while self_registration is None:
        self_registration = prompt("Enable self-registration(Y/N)").upper()
        if 'Y' in self_registration:
            self_registration = True
        elif 'N' in self_registration:
            self_registration = False
        else:
            self_registration = None
    NodeDefender.config.general.set_cfg(self_registration = self_registration)
    return True
