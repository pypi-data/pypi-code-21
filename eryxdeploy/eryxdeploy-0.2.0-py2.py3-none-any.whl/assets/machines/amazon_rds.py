from eryx_deploy.assets.machines.abs_machine import Machine


class AmazonRDSMachine(Machine):
    def install_postgresql_server(self, master_username, master_password):
        pass  # do nothing, as this machine has a ready-to-use sql server

    def install_mysql_server(self):
        pass  # do nothing, as this machine has a ready-to-use sql server
