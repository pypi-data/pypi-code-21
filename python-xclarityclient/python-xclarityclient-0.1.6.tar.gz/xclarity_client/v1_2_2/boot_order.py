from ..constants import (SYSTEM_X3550_M5, SYSTEM_X3650_M5,
                         THINKSYSTEM_SD530, THINKSYSTEM_SR630)


"""
    Boot Order Priority
"""

boot_order_priority = [
    {'name': 'singleuse', 'value': None},
    {'name': 'permanent', 'value': None},
    {'name': 'wakeonlan', 'value': None}
]

setting_boot_type = {
    'SingleUse': 'BootOrder.SingleUse',
    'Permanent': 'BootOrder.BootOrder'
}


"""
    Standard Boot Devices' names
    These name should be consistent with the ones defined in
    ironic/common/boot_devices.py
"""

PXE = 'pxe'
"Boot from PXE boot"

DISK = 'disk'
"Boot from default Hard-drive"

CDROM = 'cdrom'
"Boot from CD/DVD"

BIOS = 'bios'
"Boot into BIOS setup"

SAFE = 'safe'
"Boot from default Hard-drive, request Safe Mode"

WANBOOT = 'wanboot'
"Boot from Wide Area Network"


"""
    Boot Devices per Machine types
"""

BOOT_DEVICES = {
    SYSTEM_X3550_M5: {
        'singleuse': {
            PXE: 'PXE Network',
            DISK: 'Hard Disk 0',
            CDROM: 'CD/DVD Rom'
        },
        'permanent': {
            PXE: 'PXE Network',
            DISK: 'Hard Disk 0',
            CDROM: 'CD/DVD Rom'
        }
    },
    SYSTEM_X3650_M5: {
        'singleuse': {
            PXE: 'PXE Network',
            DISK: 'Hard Disk 0',
            CDROM: 'CD/DVD Rom'
        },
        'permanent': {
            PXE: 'PXE Network',
            DISK: 'Hard Disk 0',
            CDROM: 'CD/DVD Rom'
        }
    },
    THINKSYSTEM_SD530: {
        'singleuse': {
            PXE: 'PXE Network',
            DISK: 'Hard Disk 0',
            CDROM: 'CD/DVD Rom'
        },
        'permanent': {
            PXE: 'Network',
            DISK: 'Hard Disk',
            CDROM: 'CD/DVD Rom'
        }
    },
    THINKSYSTEM_SR630: {
        'singleuse': {
            PXE: 'PXE Network',
            DISK: 'Hard Disk 0',
            CDROM: 'CD/DVD Rom'
        },
        'permanent': {
            PXE: 'Network',
            DISK: 'Hard Disk',
            CDROM: 'CD/DVD Rom'
        }
    }
}
