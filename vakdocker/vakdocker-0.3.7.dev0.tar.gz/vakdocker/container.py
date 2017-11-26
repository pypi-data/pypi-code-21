import time
import os.path
import urllib3
import logging

import docker
from docker import client
from utils.network import get_open_port

'''
    <summary>
        This class is utility to handle everything related to dockers required
        by the consumers or producers participating in the market.
            1. Create Volume
            2. Start Container, given an image in the repo
            3. Stop Container

        In addition provides static functions to start and stop containers on
        localhost.
    </summary>
'''
class container(object):
    @staticmethod
    def local_start_container(container_url, port_map=None, volumes={}):
        dclient = docker.from_env()
        logging.info('Fetching Image: %s' % (container_url))
        image = dclient.images.pull(container_url)
        logging.info('Done Fetching Image: %s' % (container_url))
        dcont = dclient.containers.run(image.id, detach=True,
                                                ports=port_map,
                                                volumes=volumes)
        return dcont

    @staticmethod
    def local_stop_container(dcont):
        if dcont:
            logging.info('Stopping Container')
            dcont.stop()

        dclient = docker.from_env()
        dclient.containers.prune()
        dclient.images.prune()

    #Reference:
    # https://docs.docker.com/engine/extend/legacy_plugins/#volume-plugins
    @staticmethod
    def create_volume(host_url, tls_config, 
                      name=None,
                      driver=None, driver_opts=None,
                      labels=None):
        dclient = client.APIClient(base_url=host_url, tls=tls_config)
        volume = dclient.create_volume(name=name,
                                       driver=driver, driver_opts=driver_opts,
                                       labels=labels)

        return volume

    @staticmethod
    def start_container(container_url,
                        host_url, tls_config,
                        port_map=None, volumes={}, retries=5):
        urllib3.disable_warnings()
        logging.captureWarnings(True)
        dclient = client.APIClient(base_url=host_url, tls=tls_config)

        logging.info('Fetching Image: %s' % (container_url))
        image = dclient.pull(container_url)
        logging.info('Done Fetching Image: %s' % (container_url))

        while(retries > 0):
            try:
                port = None
                if port_map == None:
                    port = get_open_port()
                    port_map = {50051 : port}

                mnt_dirs = []
                for k, v in volumes.iteritems():
                    mnt_dirs.append(v.get('bind'))

                logging.info('Starting Container with Volumes: %s' \
                              % (repr(volumes)))

                container_id = dclient.create_container(
                                         container_url,
                                         './start.sh',
                                         detach=True,
                                         volumes=mnt_dirs,
                                         host_config=dclient.create_host_config(
                                                        binds=volumes,
                                                        port_bindings=port_map))
                logging.info('Done Creating Container, Id: %s' % (repr(container_id)))

                dclient.start(container_id)
                logging.info('Done Starting Container with Volumes')

                service_url = host_url.split(':')[0]
                if port:
                    service_url = host_url.split(':')[0] + ':' + str(port)

                return container_id, service_url
            except Exception, e:
                logging.error('Error: %s, \
                               Container Url: %s, \
                               Retrying for %d time' \
                               % (str(e), container_url, retries))
                retries = retries - 1

        raise Exception('Unable to Start Container')

    @staticmethod
    def stop_container(host_url, tls_config, container_id, container_url):
        dclient = client.APIClient(base_url=host_url, tls=tls_config)
        try:
            logging.info('Stopping Container')
            dclient.stop(container_id, timeout=10)
            logging.info('Removing Container and Volumes associated with it' )
            dclient.remove_container(container_id, v=True, force=True)
            logging.info('Removing Image %s' % (container_url,))
            dclient.remove_image(container_url)
            container_id = None
            logging.info('Cleanup Complete')
        except Exception, e:
            logging.info(str(e))

if __name__ == '__main__':
    DH = docker_handler(None)
    cv = DH.create_volume(name='sdk_config_vol',
                          driver='vieux/sshfs',
                          driver_opts={'sshcmd': \
                          'pankaj@client.vaksana.com:/home/pankaj/clients/sort/sdk_config',
                          'password':'passwd'},
                          labels={})

    config = {}
    config['bind'] = '/sdk_config'
    config['mode'] = 'ro'
    config['volume-driver'] = 'vieux/sshfs'
    config['volume-opt'] = {'sshcmd': 'pankaj@client.vaksana.com',
            'password':'passwd'}

    #volumes = {sdk_dir: {'bind': '/sdk_config',  'mode': 'ro'}}
    volumes = {'sdk_config_vol': config}
    DH.start_container('gargpankaj83/mongoclient', volumes=volumes)
