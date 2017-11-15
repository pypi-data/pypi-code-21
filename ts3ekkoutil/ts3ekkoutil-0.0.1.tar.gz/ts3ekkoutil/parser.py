import os
import argparse


def create_ekko_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ts3-server-host", default=os.environ.get('EKKO_TS3_SERVER_HOST', 'localhost'),
                        help="Hostname/ip of ts3 server", dest="ts3_server_host")
    parser.add_argument("--ts3-server-port", default=os.environ.get('EKKO_TS3_SERVER_PORT', "9987"),
                        help="Port of the ts3 server", dest="ts3_server_port")

    parser.add_argument("--ts3-username", default=os.environ.get('EKKO_TS3_USERNAME', "EkkoBot"),
                        help="Username of the bot", dest="ts3_username")

    parser.add_argument("--ts3-identity", default=os.environ.get('EKKO_TS3_IDENTITY', None),
                        help="Identity to be used for the bot", dest="ts3_identity")
    parser.add_argument("--ts3-uniqueid", default=os.environ.get('EKKO_TS3_UNIQUEID', None),
                        help="Unique ID, used to identify the bots own actions", dest="ts3_unique_id")
    parser.add_argument("--ts3-client-apikey", default=os.environ.get('EKKO_TS3_CLIENT_APIKEY', None),
                        help="ClientQuery apikey, configured in the ts3 client docker image", dest="ts3_client_apikey")

    parser.add_argument("--ts3-channel-name", default=os.environ.get('EKKO_TS3_CHANNEL_NAME', None),
                        help="Channel name to which the bot should connect", dest="ts3_channel_name")
    parser.add_argument("--ts3-channel-id", default=os.environ.get('EKKO_TS3_CHANNEL_ID', None),
                        help="Channel ID to which the bot should connect", dest="ts3_channel_id")
    parser.add_argument("--ts3-channel-password", default=os.environ.get('EKKO_TS3_CHANNEL_PASSWORD', None),
                        help="Channel password for the channel the bot is connecting to", dest="ts3_channel_password")
    parser.add_argument("--ts3-server-password", default=os.environ.get('EKKO_TS3_SERVER_PASSWORD'),
                        help="Password to the ts3 server", dest="ts3_server_password")
    parser.add_argument("--ts3-permission-token", default=os.environ.get('EKKO_TS3_PERMISSION_TOKEN'),
                        help="Permission token to claim rights on the ts3 server.", dest="ts3_server_permission_token")

    parser.add_argument("--ekko-media-directory", default=os.environ.get('EKKO_MEDIA_DIRECTORY', "/mnt/media/"),
                        dest="ekko_media_directory",
                        help="Directory in which files for playback from filesystem are stored")
    parser.add_argument("--teamspeak-directory",
                        default=os.environ.get('EKKO_TS3_DIRECTORY', "/opt/TeamSpeak3-Client-linux_amd64/"),
                        help="Directory in which teamspeak was installed", dest="ts3_directory")
    parser.add_argument("--teamspeak-runscript", dest="ts3_runscript",
                        default=os.environ.get('EKKO_TS3_RUNSCRIPT', "ts3client_runscript.sh"),
                        help="Filename of the runscript in the teamspeak directory (see --teamspeak-directory)")

    parser.add_argument("--ekko-manage-server", default=os.environ.get('EKKO_MANAGE_SERVER', "ts3ekkomanage"),
                        dest="ekko_manage_server_host",
                        help="Hostname/ip of the server on which the ts3ekko management instance runs")
    parser.add_argument("--ekko-manage-port", default=os.environ.get('EKKO_MANAGE_PORT', "8080"),
                        dest="ekko_manage_server_port",
                        help="Port on which the ts3ekko manage api can be reached")

    parser.add_argument("--log-level", default=os.environ.get('EKKO_LOG_LEVEL', 0))
    parser.add_argument("--log-format", help="Format in which the log messages are written",
                        default=os.environ.get('EKKO_LOG_FORMAT',
                                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    return parser
