import argparse
import docker
import os
import socket

try:
    from ts3ekkomanage.manager import TS3EkkoManage, EkkoInstanceProperties
    from ts3ekkomanage.webhooks import EkkoReverseClientContact
except ImportError:
    from .manager import TS3EkkoManage, EkkoInstanceProperties
    from .webhooks import EkkoReverseClientContact


def build_client_image(directory, tag='ekkoclient:latest'):
    docker_client = docker.from_env()
    docker_client.images.build(path=directory, tag=tag)


def entrypoint():
    parser = argparse.ArgumentParser()
    # TODO: put all of the parser into ts3ekkoutils
    parser.add_argument('--client-build-dir', default=os.environ.get('EKKO_CLIENT_BUILD_DIR', '/mnt/docker-client/'))
    parser.add_argument('--teamspeak-server', default=os.environ.get('EKKO_TS3_SERVER', 'localhost'))
    parser.add_argument('--teamspeak-port', default=os.environ.get('EKKO_TS3_PORT', '9987'))
    parser.add_argument('--base-username', default=os.environ.get('EKKO_BASE_USERNAME', 'EkkoBot'))
    parser.add_argument('--apikey', default=os.environ.get('EKKO_APIKEY', None))
    parser.add_argument('--manage-port', default=os.environ.get('EKKO_MANAGE_PORT', 8180))

    parser.add_argument('--docker-network-name', default=os.environ.get('EKKO_DOCKER_NETWORK_NAME', 'ekko_enetwork'))
    parser.add_argument('--debug-disable-autoremove', default=os.environ.get('EKKO_DEBUG_DISABLE_AUTOREMOVE', False),
                        action='store_true', dest='debug_disable_autoremove')
    args = parser.parse_args()

    args.debug_disable_autoremove = bool(args.debug_disable_autoremove)

    if args.apikey is None:
        raise AttributeError('apikey is required, please set via env or parameter')
    #FIXME: temp debug
    print(args)
    print(os.environ)
    build_client_image(args.client_build_dir)

    instance_prop = EkkoInstanceProperties(args.teamspeak_server, args.teamspeak_port, args.apikey,
                                           manage_port=args.manage_port, manage_server=socket.gethostname(),
                                           debug_disable_autoremove=args.debug_disable_autoremove,
                                           docker_network_name=args.docker_network_name)

    manage = TS3EkkoManage(instance_prop)
    ercc = EkkoReverseClientContact(manage)
    ercc.start()
    manage.start()


def main():
    entrypoint()


if __name__ == '__main__':
    main()
