import os
import argparse
from ts3ekkoutil.envconsts import EkkoPropertyNames as epn


def add_env_option(parser, name, env_name, env_default=None, **kwargs):
    parser.add_argument(name, default=os.environ.get(env_name, env_default), dest=env_name, **kwargs)


def create_ekko_parser():
    parser = argparse.ArgumentParser()
    add_env_option(parser, '--ts3-server-host', epn.TS3_SERVER_HOST, 'localhost', help='Hostname/ip of ts3 server')
    add_env_option(parser, '--ts3-server-port', epn.TS3_SERVER_PORT, '9987', help='Port of the ts3 server')

    add_env_option(parser, '--ts3-username', epn.TS3_USERNAME, 'EkkoBot', help='Username of the bot')

    add_env_option(parser, '--ts3-identity', epn.TS3_IDENTITY,
                   help='Identity to be used for the bot')
    add_env_option(parser, '--ts3-unique-id', epn.TS3_UNIQUE_ID,
                   help='Unique ID, used to identify the bots own actions')
    add_env_option(parser, '--ts3-client-apikey', epn.TS3_CLIENT_APIKEY,
                   help='ClientQuery apikey, configured in the ts3 client docker image')

    add_env_option(parser, '--ts3-channel-name', epn.TS3_CHANNEL_NAME,
                   help='Channel name to which the bot should connect')
    add_env_option(parser, '--ts3-channel-id', epn.TS3_CHANNEL_ID,
                   help='Channel ID to which the bot should connect')
    add_env_option(parser, '--ts3-channel-password', epn.TS3_CHANNEL_PASSWORD,
                   help='Channel password for the channel the bot is connecting to')
    add_env_option(parser, '--ts3-server-password', epn.TS3_SERVER_PASSWORD,
                   help='Password to the ts3 server')
    add_env_option(parser, '--ts3-server-permission-token', epn.TS3_SERVER_PERMISSION_TOKEN,
                   help='Permission token to claim rights on the ts3 server.')

    add_env_option(parser, '--ekko-media-directory', epn.EKKO_MEDIA_DIRECTORY, '/mnt/media/',
                   help='Directory in which files for playback from filesystem are stored')
    add_env_option(parser, '--teamspeak-directory', epn.TS3_DIRECTORY, '/opt/TeamSpeak3-Client-linux_amd64/',
                   help='Directory in which teamspeak was installed')
    add_env_option(parser, '--teamspeak-runscript', epn.TS3_RUNSCRIPT, 'ts3client_runscript.sh',
                   help='Filename of the runscript in the teamspeak directory (see --teamspeak-directory)')
    add_env_option(parser, '--docker-ekkoclient-directory', epn.DOCKER_EKKO_CLIENT_DIRECTORY)
    add_env_option(parser, '--docker-network-name', epn.DOCKER_NETWORK_NAME)
    add_env_option(parser, '--docker-debug-diable-autoremove', epn.DOCKER_DISABLE_AUTOREMOVE)

    add_env_option(parser, '--fixtures-path', epn.EKKO_FIXTURES_PATH,
                   help='Path of the directory which includes seed/fixture files for database initialization')

    add_env_option(parser, '--db-username', epn.DB_USERNAME)
    add_env_option(parser, '--db-password', epn.DB_PASSWORD)
    add_env_option(parser, '--db-host', epn.DB_HOST)
    add_env_option(parser, '--db-dbname', epn.DB_DBNAME)

    add_env_option(parser, '--ekko-manage-server', epn.EKKO_MANAGE_SERVER, 'ts3ekkomanage',
                   help='Hostname/ip of the server on which the ts3ekko management instance runs')
    add_env_option(parser, '--ekko-manage-port', epn.EKKO_MANAGE_PORT, '8080',
                   help='Port on which the ts3ekko manage api can be reached')

    add_env_option(parser, '--log-level', epn.LOG_LEVEL, 0)
    add_env_option(parser, '--log-format', epn.LOG_FORMAT, '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   help='Format in which the log messages are written')

    return parser
