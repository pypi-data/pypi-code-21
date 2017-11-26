import NodeDefender

def commandclasses(icpe, sensor_id, *commandclasses):
    known_classes = [commandclass.number for commandclass in \
                     NodeDefender.db.commandclass.list(icpe, sensor_id)]
    
    for commandclass in commandclasses:
        if commandclass not in known_classes:
            NodeDefender.db.commandclass.create(icpe, sensor_id, commandclass)

    for commandclass in known_classes:
        if commandclass not in commandclasses:
            NodeDefender.db.commandclass.delete(icpe, sensor_id, commandclass)
        else:
            NodeDefender.db.commandclass.update_zwave(icpe, sensor_id,
                                                      commandclass)
    return True

def commandclass_types(icpe, sensor_id, commandclass_name, *classtypes):
    try:
        known_types = NodeDefender.db.commandclass.\
                get_sql(icpe, sensor_id, classname = commandclass_name).commandclasstypes()
    except AttributeError as e:
        return False

    for classtype in classtypes:
        if classtype not in known_types:
            NodeDefender.db.commandclass.add_type(icpe, sensor_id,
                                                  commandclass_name, classtype)

    return True
