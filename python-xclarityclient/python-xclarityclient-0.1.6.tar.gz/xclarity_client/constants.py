STATE_UNKNOWN = "unknown"
STATE_POWER_ON = "power on"
STATE_POWER_OFF = "power off"
STATE_POWERING_ON = "powering_on"
STATE_POWERING_OFF = "powering_off"
STATE_STANDBY = "standby"

ACTION_POWER_ON = "powerOn"
ACTION_POWER_OFF = "powerOff"
ACTION_REBOOT = "powerCycleSoft"
ACTION_POWER_CYCLE_SOFT = "powerCycleSoft"
ACTION_POWER_CYCLE_GRACE = "powerCycleSoftGrace"


power_status_list = {
    0: STATE_UNKNOWN,
    5: STATE_POWER_OFF,
    8: STATE_POWER_ON,
    18: STATE_STANDBY
}

power_status_action = {
    ACTION_POWER_ON: 'powerOn',  # powers on the server
    ACTION_POWER_OFF: 'powerOff',  # powers off the server immediately
    ACTION_POWER_CYCLE_SOFT: 'powerCycleSoft',  # restarts the server immediately
    ACTION_POWER_CYCLE_GRACE: 'powerCycleSoftGrace',  # restarts the server gracefully
    ACTION_REBOOT: 'powerCycleSoft', # the same as powerCycleSoft
    # 'VIRTUAL_RESEAT': 'virtualReseat',  # calls the CMM function to simulate removing power from the bay
    # 'POWER_NMI': 'powerNMI',  # restarts the server with non-maskable interrupt (performs a diagnostic interrupt)
    # 'BOOT_TO_F1': 'bootToF1',  # (Lenovo endpoints only) Powers on to UEFI(F1)
}

"""
    Supported Machine Types are as below
"""

SYSTEM_X3550_M5 = 'SYSTEM X3550 M5'
SYSTEM_X3650_M5 = 'SYSTEM X3650 M5'
THINKSYSTEM_SD530 = 'THINKSYSTEM SD530'
THINKSYSTEM_SR630 = 'THINKSYSTEM SR630'

SUPPORTED_MACHINE_TYPES = [
    SYSTEM_X3550_M5,
    SYSTEM_X3650_M5,
    THINKSYSTEM_SD530,
    THINKSYSTEM_SR630
]
