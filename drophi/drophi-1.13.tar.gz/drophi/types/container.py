import logging

LOGGER = logging.getLogger(__name__)

class Container():
    "A container"
    def __init__(self, image):
        self.id = None
        self.image = image
        self.warnings = None

        self.hostname = None
        self.domainname = None
        self.user = None
        self.attachstdin = False
        self.attachstdout = True
        self.attachstderr = True
        self.ports = []
        self.tty = False
        self.openstdin = False
        self.stdinonce = False
        self.env = []
        self.cmd = []
        self.healthcheck = None
        self.args_escaped = False
        self.volumes = []
        self.working_dir = None
        self.entrypoint = None
        self.network_disabled = False
        self.mac_address = None
        self.on_build = None
        self.labels = {}
        self.stop_signal = 'SIGTERM'
        self.stop_timeout = 10
        self.shell = None
        self.host_config = None
        self.networking_config = None

    def to_payload(self):
        return {
            #'Hostname'          : self.hostname,
            #'Domainname'        : self.domainname,
            #'User'              : self.user,
            #'AttachStdin'       : self.attachstdin,
            #'AttachStdout'      : self.attachstdout,
            #'AttachStderr'      : self.attachstderr,
            #'ExposedPorts'      : self.ports,
            #'Tty'               : self.tty,
            #'OpenStdin'         : self.openstdin,
            #'StdinOnce'         : self.stdinonce,
            #'Env'               : self.env,
            #'Cmd'               : self.cmd,
            #'Healthcheck'       : self.healthcheck,
            #'ArgsEscaped'       : self.args_escaped,
            'Binds':            ['{}:{}'.format(
                v.source,
                v.target,
            ) for v in self.volumes],
            'Image'             : self.image,
            'Volumes'           : {
                v.target   : {
                    'Name'    : v.source,
                } for v in self.volumes
            },
            #'WorkingDir'        : self.working_dir,
            'Entrypoint'        : self.entrypoint,
            #'NetworkDisabled'   : self.network_disabled,
            #'MacAddress'        : self.mac_address,
            #'OnBuild'           : self.on_build,
            #'Labels'            : self.labels,
            #'StopSignal'        : self.stop_signal,
            #'StopTimeout'       : self.stop_timeout,
            #'Shell'             : self.shell,
            #'HostConfig'        : self.host_config,
            #'NetworkingConfig'  : self.networking_config,
        }

    async def run(self, client):
        payload = self.to_payload()
        result = await client.container_run(payload)
        self.id = result['Id']
        self.warnings = result['Warnings']
        LOGGER.debug("Started container %s%s", self.id, ' '.join(self.warnings) if self.warnings else '')
        return self.id
