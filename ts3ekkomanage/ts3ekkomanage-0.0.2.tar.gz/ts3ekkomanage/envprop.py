class EkkoInstanceProperties:
    def __init__(self, server, port, apikey, server_password=None, media_directory=None,
                 teamspeak_directory=None, teamspeak_runscript=None, manage_server=None, manage_port=8180,
                 docker_client_image_name='ekkoclient', base_username='Ekko Bot', fixtures_path='/mnt/fixtures/',
                 debug_disable_autoremove=None, docker_network_name='ekko_enetwork'):
        self.server = server
        self.port = port
        self.apikey = apikey
        self.base_username = base_username

        self.server_password = server_password
        self.media_directory = media_directory
        self.teamspeak_directory = teamspeak_directory
        self.teamspeak_runscript = teamspeak_runscript
        self.manage_server = manage_server
        self.manage_port = manage_port

        self.fixtures_path = fixtures_path

        self.debug_disable_autoremove = debug_disable_autoremove

        self.docker_client_image_name = docker_client_image_name
        self.docker_network_name = docker_network_name


class EkkoClientProperties:
    def __init__(self, channel_id, username, unique_id, identity, instance_prop, channel_name=None,
                 channel_password=None, permission_token=None):
        self.instance_prop = instance_prop
        self.channel_id = channel_id
        self.username = username
        self.unique_id = unique_id
        self.identity = identity

        self.channel_name = channel_name
        self.channel_password = channel_password
        self.permission_token = permission_token

    @property
    def docker_name(self):
        return self.username.replace(' ', '_')

    @property
    def docker_env(self):
        return {
            'EKKO_TS3_SERVER': self.instance_prop.server,
            'EKKO_TS3_IDENTITY': self.identity,
            'EKKO_TS3_UNIQUEID': self.unique_id,
            'EKKO_TS3_PORT': self.instance_prop.port,
            'EKKO_TS3_APIKEY': self.instance_prop.apikey,
            'EKKO_TS3_USERNAME': self.username,
            'EKKO_TS3_CHANNEL_NAME': self.channel_name,
            'EKKO_TS3_CHANNEL_ID': self.channel_id,
            'EKKO_TS3_CHANNEL_PASSWORD': self.channel_password,
            'EKKO_TS3_SERVER_PASSWORD': self.instance_prop.server_password,
            'EKKO_TS3_PERMISSION_TOKEN': self.permission_token,
            'EKKO_MEDIA_DIRECTORY': self.instance_prop.media_directory,
            'EKKO_TS3_DIRECTOY': self.instance_prop.teamspeak_directory,
            'EKKO_TS3_RUNSCRIPT': self.instance_prop.teamspeak_runscript,
            'EKKO_MANAGE_SERVER': self.instance_prop.manage_server,
            'EKKO_MANAGE_PORT': self.instance_prop.manage_port
        }
