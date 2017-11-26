import NodeDefender

def system_info(mac_address, **info):
    if info:
        NodeDefender.db.icpe.update(mac_address, **info)
    icpe = NodeDefender.db.icpe.get(mac_address)
    return {'mac_address' : icpe['mac_address'],
            'serialNumber' : icpe['serialNumber'],
            'hardware' : icpe['hardware'],
            'software' : icpe['software']}

def network_settings(mac_address, **settings):
    if settings:
        NodeDefender.db.icpe.update(mac_address, **settings)
    icpe = NodeDefender.db.icpe.get(mac_address)
    return {'ipDhcp' : icpe['ip_dhcp'],
            'ipAddress' : icpe['ip_address'],
            'ipSubnet' : icpe['ip_subnet'],
            'ipGateway' : icpe['ip_gateway']}

def time_settings(mac_address, **settings):
    pass

def battery_info(mac_address, **info):
    pass
