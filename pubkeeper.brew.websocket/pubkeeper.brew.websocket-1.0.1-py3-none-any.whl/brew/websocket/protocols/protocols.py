def get_supported_protocols():
    protocol_versions = ['v1']
    supported = {}

    for proto in protocol_versions:
        package = 'pubkeeper.brew.websocket.protocols.{}'.format(proto)
        p_module = __import__(package, fromlist=['protocol_version'])
        p_version = getattr(p_module, 'protocol_version')
        supported[p_version] = package

    return supported
