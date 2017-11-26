from flask import render_template
from flask_login import login_required, current_user
from NodeDefender.frontend.views import user_view
import NodeDefender

@user_view.route('/user/profile')
@login_required
def UserProfile():
    groups = [group.name for group in current_user.groups]
    team = NodeDefender.db.user.list(*groups)
    return render_template('frontend/user/profile.html', Team = team)

@user_view.route('/user/groups')
@login_required
def UserGroups():
    groups = [group.name for group in current_user.groups]
    team = NodeDefender.db.user.list(*groups)
    return render_template('frontend/user/groups.html', Team = team)


@user_view.route('/user/inbox')
@login_required
def UserInbox():
    return render_template('frontend/user/inbox.html')

@user_view.route('/user/inbox/<mailid>', methods=['GET', 'POST'])
@login_required
def UserInboxID(mailid):
    message = UserMessageModel.query.filter_by(uuid=mailid).first()
    return render_template('frontend/user/inboxid.html', mailid=mailid, message =
                           message)
