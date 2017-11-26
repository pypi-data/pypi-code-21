import NodeDefender.mqtt.command.icpe.zwave
import NodeDefender.mqtt.command.icpe.sys

def system_info(mac_address):
    NodeDefender.mqtt.command.icpe.sys.network.qry(mac_address)
    NodeDefender.mqtt.command.icpe.sys.network.stat(mac_address)
    NodeDefender.mqtt.command.icpe.sys.info.qry(mac_address)
    NodeDefender.mqtt.command.icpe.sys.service.qry(mac_address)
    return True

def zwave_info(mac_address):
    NodeDefender.mqtt.command.icpe.zwave.info.qry(mac_address)
    NodeDefender.mqtt.command.icpe.zwave.node.list(mac_address)
    return True


def include_mode(mac_address):
    NodeDefender.mqtt.command.icpe.zwave.mode.include(mac_address)
    return True

def exclude_mode(mac_address):
    NodeDefender.mqtt.command.icpe.zwave.mode.exclude(mac_address)
    return True

