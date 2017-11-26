from NodeDefender import socketio

def event(mac_address, sensor_id, data):
    socketio.emit('event', (mac_address, sensor_id, data),
                  namespace='/icpe'+mac_address, broadcast=True)
