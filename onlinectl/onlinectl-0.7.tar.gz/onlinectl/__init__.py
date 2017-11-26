#!/usr/bin/env python
import requests
import slumber
import logging
import sys
import json


class OnlineCtl():
    """
        PythonClass to interact with online.net API
    """

    def __init__(self, token, url='https://api.online.net/api/v1'):
        """
            Initialize connexion with Online API
        """

        self.api_session = requests.session()
        self.token = 'Bearer ' + token
        self.api_url = url
        self.api_session.headers['Authorization'] = self.token
        self.api = slumber.API(
                self.api_url, session=self.api_session, append_slash=False)

    def get_lists_of_servers(self):

        servers_list = []
        api_server_endpoint = self.api_url + '/server/'
        logging.debug("Call {}".format(api_server_endpoint))
        for i in self.api_session.get(api_server_endpoint).json():
            logging.debug(i.split('/')[-1])
            server = self.api_session.get(
                    api_server_endpoint + i.split('/')[-1])
            logging.debug(api_server_endpoint + i.split('/')[-1])
            servers_list.append(server.json())
        self.servers_list = servers_list
        return(servers_list)

    def get_available_os(self, server_id):

        try:
            int(server_id)
        except Exception as e:
            print("server_id must be an integer : {}".format(e))
        os_list = self.api.server.operatingSystems(server_id).get()
        return os_list

    def get_sshkeys(self):

        ssh_keys = self.api.user.key.ssh.get()
        return ssh_keys

    def put_sshkeys(self, pubkey):

        pass

    def install_server(
            self, server_id, os_id, hostname, user_login,
            user_password, root_password, pannel_password, ssh_keys,
            partition_template=None, partition=None):

        api_server_endpoint = self.api_url + '/server/install/' + server_id

        if partition_template is not None:
            logging.debug("Using partition template")

            server_configuration = {
                    'os_id': os_id, 'hostname': hostname,
                    'user_login': user_login, 'user_password': user_password,
                    'root_password': root_password,
                    'pannel_password': pannel_password, 'ssh_keys': [ssh_keys],
                    'partitioning_template_ref': partition_template
                    }

        elif partition is not None:
            logging.debug("Using partition")

            if type(partition) == str:
                partition = json.loads(partition.replace("'", "\""))

                logging.debug("Change partition type, now is {}".format(
                    type(partition)))

            server_configuration = {
                    'os_id': os_id, 'hostname': hostname,
                    'user_login': user_login, 'user_password': user_password,
                    'root_password': root_password,
                    'pannel_password': pannel_password, 'ssh_keys': [ssh_keys],
                    'partitioning': partition
                    }
        else:
            logging.error("You must use partition_template or partitioning")
            sys.exit(1)
        logging.debug(server_configuration)

        try:
            install_server_call = self.api_session.post(
                    api_server_endpoint, json=server_configuration)
        except Exception as e:
            logging.error("Error: {}".format(e))

        if (install_server_call.status_code != 200 and
                install_server_call.status_code != 201):
            status_code = install_server_call.status_code
            server_call_return = install_server_call.json()
            logging.error("{}: Error: {}, Code: {}".format(
                status_code, server_call_return['code'],
                server_call_return['error']))
        elif install_server_call.status_code == 201:
            return {'status': 'ok'}

    def reboot_server(self, server_id, reason=None, email=None):
        api_server_endpoint = self.api_url + '/server/reboot/' + server_id

        reboot_parameter = {'reason': reason, 'email': email}
        try:
            reboot_server_call = self.api_session.post(
                    api_server_endpoint, json=reboot_parameter)
        except:
            pass
        if (reboot_server_call.status_code != 200 and
                reboot_server_call.status_code != 201):
            status_code = reboot_server_call.status_code
            server_call_return = reboot_server_call.json()
            logging.error("{}: Error: {}, Code: {}".format(
                status_code, server_call_return['code'],
                server_call_return['error']))
        elif reboot_server_call.status_code == 201:
            return {'status': 'ok'}

    def move_fip(self, source, destination=None):
        api_server_endpoint = self.api_url + '/server/failover/edit'
        try:
            move_fip = self.api_session.post(
                    api_server_endpoint, json={'source': source,
                        'destination': destination})
        except:
            pass
        if (move_fip.status_code != 200 and
                move_fip.status_code != 201):
            status_code = move_fip.status_code
            server_call_return = move_fip.json()
            logging.error("{}: Error: {}, Code: {}".format(
                status_code, server_call_return['code'],
                server_call_return['error']))
        elif move_fip.status_code == 201:
            return {'status': 'ok'}
