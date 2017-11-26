from flask_script import Manager, prompt
import NodeDefender

manager = Manager(usage='Manage iCPE Devices')

@manager.option('-m', '--mac', dest='mac', default=None)
def delete(mac):
    'Delete iCPE'
    if mac is None:
        mac = prompt('Mac')

    try:
        NodeDefender.db.icpe.delete(mac)
    except LookupError as e:
        print("Error: ", str(e))
        return
    print("Successfully Deleted: ", mac)

@manager.command
def list():
    'List iCPEs'
    icpes = NodeDefender.db.icpe.list()
    if not icpes:
        print("No icpes")
        return False

    for icpe in icpes:
        print("ID: {}, MAC: {}".format(icpe.id, icpe.mac_address))
    return True

@manager.command
def unassigned():
    icpes = NodeDefender.db.icpe.unassigned()
    if not icpes:
        print("No Unassigned iCPEs")
        return False

    for icpe in icpes:
        print("ID: {}, MAC: {}".format(icpe.id, icpe.mac_address))
    return True

@manager.option('-mac', '--mac', dest='mac', default=None)
def info(mac):
    'Info about a specific iCPE'
    if mac is None:
        mac = prompt('Mac')
    
    icpe = NodeDefender.db.icpe.get_sql(mac)
    if icpe is None:
        print("Unable to find iCPE {}".format(mac))

    print('ID: {}, MAC: {}'.format(icpe.id, icpe.mac_address))
    print('Alias {}, Node: {}'.format(icpe.alias, icpe.node.name))
    print('ZWave Sensors: ')
    for sensor in icpe.sensors:
        print('Alias: {}, Type: {}'.format(sensor.alias, sensor.type))
