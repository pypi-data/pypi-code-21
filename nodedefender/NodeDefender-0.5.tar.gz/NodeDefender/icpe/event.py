import NodeDefender

def system_status(mac_address, payload):
    operation, status = payload['stat'].split(',')
    if operation == '0' and status == '0':
        pass
    elif operation == '1' and status == '0':
        pass
    elif operation == '2' and status == '0':
        pass
    elif operation == '3':                      # Node Excluded
        if status == '0':                       # Operation successful
            NodeDefender.mqtt.command.icpe.zwave.node.list(mac_address)
    elif operation == '4' and status == '0':
        pass
    elif operation == '5':                      # Node removed
        if status == '0':                       # Operation successful
            NodeDefender.mqtt.command.icpe.zwave.node.list(mac_address)
    elif operation == '6' and status == '0':
        pass
    elif operation == '7' and status == '0':
        pass
    elif operation == '8' and status == '0':
        pass
    elif operation == '9' and status == '0':
        pass
    elif operation == '10' and status == '0':
        pass
    elif operation == '11' and status == '0':
        pass
    elif operation == '13' and status == '0':
        pass
    elif operation == '14' and status == '0':
        pass
    elif operation == '15' and status == '0':
        pass
    elif operation == '50' and status == '0':
        pass
    elif operation == '51' and status == '0':
        pass

    home_id = payload['netid']
    controller_id = payload['controllerid']
    
    automatic_polling = bool(eval(payload['aopoll']))
    always_reporting = bool(eval(payload['awrpt']))
    general_wakeup = payload['acwkup']
    forward_unsolicited = bool(eval(payload['unsolicit']))
    #auto_reboot = bool(eval(payload['armask']))
    auto_isolate = bool(eval(payload['autoisolate']))
    battery_warning = bool(eval(payload['bnlevel']))
    health_check_interval = payload['hcinterval']
    NodeDefender.db.icpe.update_redis(mac_address,
                                 home_id = home_id,
                                 controller_id = controller_id,
                                 automatic_polling = automatic_polling,
                                 always_reporting = always_reporting,
                                 general_wakeup = general_wakeup,
                                 forward_unsolicited = forward_unsolicited,
                                 #auto_reboot = auto_reboot,
                                 auto_isolate = auto_isolate,
                                 battery_warning = battery_warning,
                                 health_check_interval = health_check_interval)
    return True
