def config_file_dic():
    import ConfigParser
    parser = ConfigParser.ConfigParser()
    parser.read("/etc/ext_cloud/ext_cloud.conf")
    if not parser.has_section('openstack'):
        return None
    dic = {}
    for arg in parser.options('openstack'):
        dic[arg] = parser.get('openstack', arg)

    return dic
