import arrow

class DockerObject():
    PROPERTIES = ()
    def __eq__(self, other):
        return all([getattr(self, p) == getattr(other, p) for p in self.PROPERTIES])

    def diff(self, other):
        return {
            p: (getattr(self, p), getattr(other, p))
            for p in self.PROPERTIES if getattr(self, p) != getattr(other, p)
        }

class Container():
    "A container"
    def __init__(self, image):
        self.image = image

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
        self.labels = []
        self.stop_signal = 'SIGTERM'
        self.stop_timeout = 10
        self.shell = None
        self.host_config = None
        self.networking_config = None

    def get_create_payload(self):
        return {
            'Hostname'          : self.hostname,
            'Domainname'        : self.domainname,
            'User'              : self.user,
            'AttachStdin'       : self.attachstdin,
            'AttachStdout'      : self.attachstdout,
            'AttachStderr'      : self.attachstderr,
            'ExposedPorts'      : self.ports,
            'Tty'               : self.tty,
            'OpenStdin'         : self.opnstdin,
            'StdinOnce'         : self.stdinonce,
            'Env'               : self.env,
            'Cmd'               : self.cmd,
            'Healthcheck'       : self.healthcheck,
            'ArgsEscaped'       : self.args_escaped,
            'Image'             : self.image,
            'Volumes'           : [v.to_payload() for v in self.volumes],
            'WorkingDir'        : self.working_dir,
            'Entrypoint'        : self.entrypoint,
            'NetworkDisabled'   : self.network_disabled,
            'MacAddress'        : self.mac_address,
            'OnBuild'           : self.on_build,
            'Labels'            : self.labels,
            'StopSignal'        : self.stop_signal,
            'StopTimeout'       : self.stop_timeout,
            'Shell'             : self.shell,
            'HostConfig'        : self.host_config,
            'NetworkingConfig'  : self.networking_config,
        }

class Port():
    def __init__(self, name, published, target, protocol='tcp', mode='ingress'):
        self.name       = name
        self.protocol   = protocol
        self.mode       = mode
        self.published  = published
        self.target     = target

    def __eq__(self, other):
        return all([getattr(self, p) == getattr(other, p) for p in (
            'protocol', 'mode', 'published', 'target')])

    @staticmethod
    def parse(payload):
        return Port(
            mode        = payload['PublishMode'],
            name        = payload.get('Name'),
            protocol    = payload['Protocol'],
            published   = payload['PublishedPort'],
            target      = payload['TargetPort'],
        )

    def to_service_payload(self):
        return {
            'Name'              : self.name,
            'Protocol'          : self.protocol,
            'PublishedPort'     : self.published,
            'TargetPort'        : self.target,
        }

