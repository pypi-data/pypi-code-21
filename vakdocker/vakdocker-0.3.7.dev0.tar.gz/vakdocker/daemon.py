import os.path
import logging
from subprocess import Popen, PIPE
from distutils.spawn import find_executable

import docker
from docker import client
from utils.openssl_keys import openssl_keys

'''
    <summary>
        This class helps any one (with docker installed) start and stop docker
        hosting service securely.
        Also, this allows the host to generate set of keys for any client who
        can potentially launch/contain container services on the host.
    </summary>
'''
class daemon(object):
    '''
        <summary>
            This functions generates the SSL keys and starts the secure docker
            hosting service. The keys are stored in the ssl_keys_dir passed.

            The keys are used subsequently to generate client keys as well.
        </summary>
    '''
    @staticmethod
    def start_daemon(hostname, port, ssl_keys_dir):
        if not os.path.exists(ssl_keys_dir):
            os.makedirs(ssl_keys_dir)

        sslkeys_obj = openssl_keys(ssl_keys_dir)
        tls_cacert = sslkeys_obj.get_authcertificate()

        keypath = os.path.join(ssl_keys_dir, 'server.pem')
        certpath = os.path.join(ssl_keys_dir, 'server.cert')
        if os.path.isfile(keypath) == False or \
           os.path.isfile(certpath):
            pkey, cert = sslkeys_obj.generate_pair(hostname, 'server')
            open(keypath, 'w').write(pkey)
            open(certpath, 'w').write(cert)

        #TODO: Check if some daemon is already running
        service = []
        dockerd_bin = os.path.abspath(find_executable('dockerd'))
        service.append(dockerd_bin)
        service.append('--tlsverify')
        service.append('--tlscacert=' + tls_cacert)
        service.append('--tlskey=' + keypath)
        service.append('--tlscert=' + certpath)
        service.append('-H=0.0.0.0:' + str(port))
        service.append('-H=unix:///var/run/docker.sock')

        dockerd = Popen(service, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        return dockerd

    '''
        <summary>
            Using the private keys generated at the time of starting the
            service to generate key pair for the clients who can controll all
            the services running on the host.

            The keys should be shared with only trustworthy clients. With these
            keys clients can potentially gain root access to the machine.
        </summary>
    '''
    @staticmethod
    def get_client_tlskeys(hostname, ssl_keys_dir):
        sslkeys_obj = openssl_keys(ssl_keys_dir)

        tls_cacert = sslkeys_obj.get_authcertificate()
        cacert = file(tls_cacert).read()
        pkey, cert = sslkeys_obj.generate_pair(hostname, 'client')
        return (pkey, cert, cacert)

    '''
        <summary>
            Stops the Docker Daemon
        </summary>
    '''
    @staticmethod
    def stop_daemon():
        service = []
        pkill_bin = os.path.abspath(find_executable('pkill'))
        service.append(pkill_bin)
        service.append('-f')
        service.append('dockerd')
        killp = Popen(service, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        killp.wait()


if __name__ == '__main__':
    daemon.start_daemon('client.vaksana.com', 2376, '/home/pankaj/.docker/')
    #daemon.stop_daemon()
