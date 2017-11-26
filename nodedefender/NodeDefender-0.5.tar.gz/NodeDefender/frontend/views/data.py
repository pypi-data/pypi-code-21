from NodeDefender.frontend.views import data_view
from flask import request, render_template
from NodeDefender import serializer
from flask_login import login_required, current_user
import NodeDefender

#Power
@data_view.route('/data/power')
@login_required
def data_power():
    if request.method == 'GET':
        groups = NodeDefender.db.group.list(current_user.email)
        return render_template('frontend/data/power.html', groups = groups)

@data_view.route('/data/power/group/<name>')
@login_required
def power_group(name):
    name = serializer.loads(name)
    if request.method == 'GET':
        group = NodeDefender.db.group.get(name)
        if group is None:
            pass # Fix later..
        return render_template('frontend/data/group/power.html', group = group)

@data_view.route('/data/power/node/<name>')
@login_required
def power_node(name):
    name = serializer.loads(name)
    if request.method == 'GET':
        node = NodeDefender.db.node.get(name)
        return render_template('frontend/data/node/power.html', node = node)

@data_view.route('/data/power/sensor/<icpe>/<sensor>')
@login_required
def power_sensor(icpe, sensor):
    icpe = serializer.loads(icpe)
    
    if request.method == 'GET':
        sensor = NodeDefender.db.sensor.get(icpe, sensor)
        return render_template('frontend/data/sensor/power.html', sensor = sensor)

#Heat
@data_view.route('/data/heat')
@login_required
def data_heat():
    if request.method == 'GET':
        groups = NodeDefender.db.group.list(current_user.email)
        return render_template('frontend/data/heat.html', groups = groups)

@data_view.route('/data/heat/group/<name>')
@login_required
def heat_group(name):
    name = serializer.loads(name)
    if request.method == 'GET':
        group = NodeDefender.db.group.get(name)
        if group is None:
            pass # Fix later..
        return render_template('frontend/data/group/heat.html', group = group)

@data_view.route('/data/heat/node/<name>')
@login_required
def heat_node(name):
    name = serializer.loads(name)
    if request.method == 'GET':
        node = NodeDefender.db.node.get(name)
        return render_template('frontend/data/node/heat.html', node = node)

@data_view.route('/data/heat/sensor/<icpe>/<sensor>')
@login_required
def heat_sensor(icpe, sensor):
    icpe = serializer.loads(icpe)
    
    if request.method == 'GET':
        sensor = NodeDefender.db.sensor.get(icpe, sensor)
        return render_template('frontend/data/sensor/heat.html', sensor = sensor)
