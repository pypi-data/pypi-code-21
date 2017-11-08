import docker
import asyncio
import argparse
import logging

from sqlalchemy_seed import load_fixtures, load_fixture_files

try:
    from ts3ekkomanage.webhooks import EkkoReverseClientContact
    from ts3ekkomanage.envprop import EkkoClientProperties, EkkoInstanceProperties
    from ts3ekkomanage.model import session, Identity
except ImportError:
    from .webhooks import EkkoReverseClientContact
    from .envprop import EkkoClientProperties, EkkoInstanceProperties
    from .model import session, Identity


class EkkoNoIdentityAvailable(Exception):
    def __str__(self):
        return "There is no unused identity avilable."


class TS3EkkoManage():
    def __init__(self, instance_prop, loop=None, seed_data=True, spawn_first_client=True):
        self.loop = loop or asyncio.get_event_loop()
        self.reverse_client_contact = EkkoReverseClientContact(self)
        self.docker_conn = docker.from_env()

        self.instance_prop = instance_prop
        self.clients = []

        logging.info('TESTTEST')

        if seed_data:
            self.seed_fixtures()

        if spawn_first_client:
            self.spawn()

    def spawn(self, channel_id=None, channel_password=None):
        # get list of clients
        # check if a client is already in this channel
        # if not, then create new docker container from image and params
        for client in self.clients:
            if channel_id == client.channel_id:
                return
        logging.info(self.clients)
        try:
            new_identity = self.find_unused_identity()

            new_client = EkkoClientProperties(channel_id=0,
                                              username=f'{self.instance_prop.base_username} {len(self.clients)+1}',
                                              unique_id=new_identity.unique_ts3_id, identity=new_identity.unique_ts3_id,
                                              instance_prop=self.instance_prop)

            self.docker_conn.containers.run(image=self.instance_prop.docker_client_image_name, detach=True,
                                            name=new_client.docker_name, environment=new_client.docker_env,
                                            auto_remove=not self.instance_prop.debug_disable_autoremove,
                                            network=self.instance_prop.docker_network_name, links=[('db', 'dbhost')])
        except EkkoNoIdentityAvailable as e:
            # TODO: add response to invoker
            logging.warning(e)
            print(e)

    def despawn(self, channel_id, unique_id):
        # get the client who is in the channel
        # kill it
        for client in self.clients:
            if unique_id == client.unique_id and channel_id == client.channel_id:
                self.docker_conn.stop(client.docker_name)
        pass

    def register_move(self, new_channel, unique_id):
        # TODO need to define behavior
        pass

    def find_unused_identity(self):
        all_identities = session.query(Identity)
        used_identities = [client.identitiy for client in self.clients]
        unused_identities = [ident for ident in all_identities if ident.private_identity not in used_identities]
        if unused_identities != []:
            return unused_identities[0]
        else:
            raise EkkoNoIdentityAvailable()

    def seed_fixtures(self):
        fixtures = load_fixture_files(self.instance_prop.fixtures_path, ['identities.yaml'])
        load_fixtures(session, fixtures)

    async def periodic_update(self, delay=10):
        while True:
            print(1)
            await asyncio.sleep(delay)

    def start(self):
        self.reverse_client_contact.start()
        self.loop.run_until_complete(
            asyncio.wait([
                self.periodic_update(),
            ])
        )
