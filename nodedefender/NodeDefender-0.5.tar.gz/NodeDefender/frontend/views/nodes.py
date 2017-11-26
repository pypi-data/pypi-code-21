from NodeDefender.frontend.views import node_view
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from NodeDefender.frontend.forms.node import (LocationForm, iCPEForm, SensorForm,
NodeCreateForm)
from NodeDefender import serializer
import NodeDefender

@node_view.route('/nodes/list', methods=['GET', 'POST'])
@login_required
def nodes_list():
    if request.method == 'GET':
        groups = NodeDefender.db.group.list(current_user.email)
        nodes = NodeDefender.db.node.list(*[group.name for group in groups])
        if current_user.superuser:
            nodes = nodes + NodeDefender.db.node.unassigned()
        return render_template('frontend/nodes/list.html', nodes = nodes)
    else:
        CreateForm.validate_on_submit()
        try:
            node = NodeSQL.Create(
                CreateForm.Name.data,
                location)
            NodeDefender.db.node.location(CreateForm.Name.data,\
                                          CreateForm.Street.data,\
                                          CreateForm.City.data)
            iCPE = NodeDefender.db.icpe.get_sql(CreateForm.Mac.data)
            if iCPE:
                NodeDefender.db.node.add_icpe(node.name, \
                                             iCPE.mac_address)
            if CreateForm.Group.data:
                NodeDefender.db.group.add_node(CreateForm.Group.data,\
                                              node.name)
        except LookupError as e:
            flash("Error Creating Node: " + str(e), 'danger')
            return redirect(url_for('node_view.NodesList'))
        url = url_for("node_view.nodes_node", name =
                      serializer.dumps(node.name))
        flash('Succesfully added node: ' + node.name, 'success')
        return redirect(url)

@node_view.route('/nodes/<name>', methods=['GET', 'POST'])
@login_required
def nodes_node(name):
    name = serializer.loads(name)
    node = NodeDefender.db.node.get(name)
    if request.method == 'GET':
        return render_template('frontend/nodes/node.html', Node = node)
    
    if icpeform.Submit.data and icpeform.validate_on_submit():
        icpe.alias = BasicForm.alias.data
        icpe.comment = BasicForm.comment.data
    elif locationform.Submit.data and locationform.validate_on_submit():
        icpe.location.street = AddressForm.street.data
        icpe.location.city = AddressForm.city.data
        icpe.location.geolat = AddressForm.geolat.data
        icpe.location.geolong = AddressForm.geolong.data

    db.session.add(icpe)
    db.session.commit()
    return render_template('frontend/nodes/node.html', Node = node)

'''
@node_view.route('/nodes/list/<mac_address>/<sensor_id>', methods=['GET', 'POST'])
@login_required
def sensor_configure(mac_address, nodeid):
    icpe = NodeDefender.db.icpe.get_sql(mac_address)
    if icpe is None:
        return redirect(url_for('index'))
    NodeBasic = NodeBasicForm()
    if request.method =='POST':
        try:
            ZNode = [node for node in icpe.znodes if node.nodeid == int(nodeid)][0]
        except IndexError:
            print('could not find ZWave NOde')
            return redirect(url_for('NodesNode', mac=mac))
        icpe.UpdateNodeInfo(**{'Alias' :  NodeBasic.alias.data, 'mac' : mac, 'nodeid' : nodeid})
        ZNode.alias = NodeBasic.alias.data
        db.session.add(ZNode)
        db.session.commit()
        return redirect(url_for('NodesNode', mac=mac))
    return redirect(url_for('NodesNode', mac=mac))


@node_view.route('/nodes/<mac>/notes/add', methods=['GET', 'POST'])
@login_required
def NodesNotesAdd(mac):
    if request.method == 'POST':
        note = request.form['note']
        icpe = iCPEModel.query.filter_by(mac_address = mac).first()
        dbnote = NodeNotesModel(current_user.email, note)
        icpe.notes.append(dbnote)
        db.session.add(icpe)
        db.session.commit()
        return redirect(url_for('NodesNode', mac=mac))
    else:
        return redirect(url_for('NodesNode', mac=mac))

@node_view.route('/nodes/<mac>/notes/sticky', methods=['GET', 'POST'])
@login_required
def NodesNoteSticky(mac):
    if request.method == 'POST':
        note = request.form['note']
        icpe = iCPEModel.query.filter_by(mac_address = mac).first()
        icpe.notesticky = note
        db.session.add(icpe)
        db.session.commit()
        return redirect(url_for('NodesNode', mac=mac))
    else:
        return redirect(url_for('NodesNode', mac=mac))

@node_view.route('/nodes/<mac>/delete')
@login_required
def DeleteNode(mac):
    try:
        icpe.DeleteiCPE(mac)
        flash('Node: ' + mac + ' successfully deleted', 'success')
        return redirect(url_for('NodesList'))
    except Exception as e:
        flash('Unable to remove ' + str(mac) + '. Error: ' + str(e), 'danger')
        return redirect(url_for('NodesList'))
'''

