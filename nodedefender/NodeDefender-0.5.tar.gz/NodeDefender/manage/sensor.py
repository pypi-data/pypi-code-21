from flask_script import Manager, prompt
import NodeDefender

manager = Manager(usage='Manage Sensors')

@manager.option('-m', '--mac', dest='mac', default=None)
@manager.option('-i', '--id', dest='index', default=None)
def delete(mac, index):
    'Delete Sensor'
    if mac is None:
        mac = prompt('Mac')
    if index is None:
        index = prompt('Index')

    try:
        sensor.Delete(index, mac)
    except LookupError as e:
        print("Error: ", str(e))
        return

    print("Successfully Deleted: ", sensor)

@manager.command
def purge():
    'Purge Sensors'
    for s in sensor.List():
        SQL.session.delete(s)
    SQL.session.commit()
    print("Sensors succesfully purged")

@manager.command
def list():
    'List Sensors'
    for s in sensor.List():
        print("ID: {}, Name: {}".format(s.id, s.name))
        print("MAC: {}, Sensor ID: {}".format(s.icpe.mac_address, s.sensor_id))
        print("-------------")

@manager.option('-m', '--mac', dest='mac', default=None)
@manager.option('-i', '--index', dest='index', default=None)
def info(mac, index):
    'Info about a specific Sensor'
    if mac is None:
        mac = prompt('mac')
    if index is None:
        index = prompt('Index')

    s = sensor.Get(mac, index)
    if icpe is None:
        print("Unable to find iCPE {}".format(mac))

    print('ID: {}, Name: {}'.format(s.id, s.name))
    print('iCPE: {}, Mac: {}'.format(s.icpe.name, s.icpe.mac_address))
