from NodeDefender.db.sql import SQL, UserModel, GroupModel
import NodeDefender

def get_sql(email):
    return UserModel.query.filter_by(email = email).first()

def update_sql(email, **kwargs):
    user = get_sql(email)
    if user is None:
        return False
    for key, value in kwargs.items():
        if key not in user.columns():
            continue
        setattr(user, key, value)
    SQL.session.add(user)
    SQL.session.commit()
    return user

def create_sql(email):
    if get_sql(email):
        return get_sql(email)
    user = UserModel(email)
    SQL.session.add(user)
    SQL.session.commit()
    return user

def save_sql(user):
    SQL.session.add(user)
    SQL.session.commit()
    return user

def delete_sql(email):
    if not get_sql(email):
        return False
    SQL.session.delete(get_sql(email))
    SQL.session.commit()
    return True

def get(email):
    return get_sql(email)

def set_password(email, raw_password):
    user = get_sql(email)
    user.password = NodeDefender.bcrypt.\
            generate_password_hash(raw_password).decode('utf-8')
    return save_sql(user)

def enable(email):
    user = get_sql(email)
    user.enabled = True
    return save_sql(user)

def disable(email):
    user = get_sql(email)
    user.enabled = False
    return save_sql(user)

def groups(email):
    try:
        return get_sql(email).groups
    except AttributeError:
        return []

def set_role(email, role):
    user = get_sql(email)
    user.set_role(role)
    SQL.session.add(user)
    SQL.session.commit()
    return user

def get_role(email):
    return get_sql(email).role()

def list(*group_names):
    if not group_names:
        return [user for user in UserModel.query.all()]
    return [user for user in \
            SQL.session.query(UserModel).join(UserModel.groups).\
            filter(GroupModel.name.in_(group_names)).all()]

def create(email, firstname = None, lastname = None):
    create_sql(email)
    update_sql(email, **{'firstname' : firstname, 'lastname' : lastname})
    user = get_sql(email)
    NodeDefender.db.message.user_created(user)
    return user

def update(email, **kwargs):
    return update_sql(email, **kwargs)

def delete(email):
    return delete_sql(email)
