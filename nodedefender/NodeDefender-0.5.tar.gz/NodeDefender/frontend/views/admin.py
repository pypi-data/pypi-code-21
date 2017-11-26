from NodeDefender.frontend.views import admin_view
from NodeDefender.frontend.forms.admin import (GeneralForm, CreateUserForm, CreateGroupForm,
                    CreateMQTTForm, UserSettings, UserPassword, UserGroupAdd)
from NodeDefender.frontend.forms.group import ModifyGeneral
from flask_login import login_required, current_user
from flask import Blueprint, request, render_template, flash, redirect, url_for
from NodeDefender import serializer
import NodeDefender

@admin_view.route('/admin/server', methods=['GET', 'POST'])
@login_required
def admin_server():
    MQTTList = NodeDefender.db.mqtt.list(user = current_user.email)
    MQTT = CreateMQTTForm()
    if request.method == 'GET':
        return render_template('frontend/admin/server.html',
                               MQTTList = MQTTList, MQTTForm = MQTT)
    if MQTT.Submit.data and MQTT.validate_on_submit():
        try:
            NodeDefender.db.mqtt.create(MQTT.IPAddr.data, MQTT.Port.data)
            NodeDefender.mqtt.connection.add(MQTT.IPAddr.data, MQTT.Port.data)
        except ValueError as e:
            flash('Error: {}'.format(e), 'danger')
            return redirect(url_for('admin_view.admin_server'))
    
    if General.Submit.data and General.validate_on_submit():
        flash('Successfully updated General Settings', 'success')
        return redirect(url_for('admin_server'))
    else:
        flash('Error when trying to update General Settings', 'danger')
        return redirect(url_for('admin_view.admin_server'))

    flash('{}'.format(e), 'success')
    return redirect(url_for('admin_view.admin_server'))

@admin_view.route('/admin/groups', methods=['GET', 'POST'])
@login_required
def admin_groups():
    GroupForm = CreateGroupForm()
    groups = NodeDefender.db.group.list(user_mail = current_user.email)
    if request.method == 'GET':
        return render_template('frontend/admin/groups.html', groups = groups,
                                CreateGroupForm = GroupForm)
    else:
        if not GroupForm.validate_on_submit():
            flash('Form not valid', 'danger')
            return redirect(url_for('admin_view.admin_groups'))
        try:
            group = NodeDefender.db.group.create(GroupForm.Name.data)
            NodeDefender.db.group.update(group.name, **\
                                         {'email' : GroupForm.Email.data,
                                          'description' :
                                          GroupForm.description.data})
        except ValueError as e:
            flash('Error: {}'.format(e), 'danger')
            return redirect(url_for('admin_view.admin_groups'))
        flash('Successfully Created Group: {}'.format(group.name), 'success')
        return redirect(url_for('admin_view.admin_group', name =
                                serializer.dumps(group.name)))

@admin_view.route('/admin/groups/<name>')
@login_required
def admin_group(name):
    name = serializer.loads(name)
    group = NodeDefender.db.group.get(name)
    if group is None:
        flash('Group {} not found'.format(name), 'danger')
        return redirect(url_for('admin_view.admin_groups'))
    return render_template('frontend/admin/group.html', Group = group)

@admin_view.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    UserForm = CreateUserForm()
    if request.method == 'GET':
        if current_user.superuser:
            users = NodeDefender.db.user.list()
        else:
            groups = NodeDefender.db.group.list(current_user.email)
            groups = [group.name for group in groups]
            users = NodeDefender.db.user.list(*groups)
        return render_template('frontend/admin/users.html', Users = users,\
                               CreateUserForm = UserForm)
    if not UserForm.validate():
        flash('Error adding user', 'danger')
        return redirect(url_for('admin_view.admin_users'))
    try:
        user = NodeDefender.db.user.create(UserForm.Email.data,
                                           UserForm.Firstname.data,
                                           UserForm.Lastname.data)
    except ValueError as e:
        flash('Error: {}'.format(e), 'danger')
        redirect(url_for('admin_view.admin_users'))
    flash('Successfully added user {}'.format(user.firstname), 'success')
    return redirect(url_for('admin_view.admin_user', email = user.email))

@admin_view.route('/admin/users/<email>', methods=['GET', 'POST'])
@login_required
def admin_user(email):
    email = serializer.loads(email)
    usersettings = UserSettings()
    userpassword = UserPassword()
    usergroupadd = UserGroupAdd()
    user = NodeDefender.db.user.get(email)
    if request.method == 'GET':
        if user is None:
            flash('User {} not found'.format(id), 'danger')
            return redirect(url_for('admin_view.admin_groups'))
        return render_template('frontend/admin/user.html', User = user, UserSettings =
                               usersettings, UserPassword = userpassword,
                               UserGroupAdd = usergroupadd)
    
    if usersettings.Email.data and usersettings.validate():
        NodeDefender.db.user.update(usersettings.Email.data, **\
                                    {'firstname' : usersettings.Firstname.data,
                                     'lastname' : usersettings.Lastname.data})
        return redirect(url_for('admin_view.admin_user', email =
                                serializer.dumps(usersettings.Email.data)))

@admin_view.route('/admin/backup')
@login_required
def admin_backup():
    return render_template('frontend/admin/backup.html')
