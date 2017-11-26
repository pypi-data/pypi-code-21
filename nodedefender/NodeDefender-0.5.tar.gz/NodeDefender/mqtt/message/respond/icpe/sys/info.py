import NodeDefender

def qry(topic, payload):
    mac = payload.pop(0)
    sn = payload.pop(0)
    mdata = payload.pop(0)
    hw = payload.pop(0)
    sw = payload.pop(0)

    uptime = payload.pop(2)
    local_time = payload.pop(2)
    return NodeDefender.db.icpe.update(topic['mac_address'],
                                       **{'serial_number' : sn,
                                          'hardware' : hw,
                                          'firmware' : sw})
