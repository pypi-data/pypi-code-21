import sys, os
import platform
import json
import time
sys.path.append(os.getcwd())

counter = 1
from sys import stdout, path
from omsdk.sdkcreds import UserCredentials,ProtocolCredentialsFactory
from omsdk.sdkprint import PrettyPrint
from omsdk.sdkfile import FileOnShare, LocalFile
from omsdk.sdkenum import MonitorScopeFilter, MonitorScope
from omsdk.sdkproto import ProtocolEnum
from omsdk.sdkinfra import sdkinfra
from omsdk.sdkprotopref import ProtoPreference, ProtocolEnum, ProtoMethods
from omsdk.catalog.sdkupdatemgr import UpdateManager
import logging
from omsdk.omlogs.Logger import LogManager, LoggerConfigTypeEnum
from omdrivers.enums.iDRAC.iDRACEnums import *
from omdrivers.helpers.iDRAC.UpdateHelper import UpdateHelper
from omsdk.sdkproto import Simulator

Simulator.start_simulating()

#LogManager.setup_logging()

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

# Bugs: not element>>#cdata-section

###############################
# Local Functions
###############################
def _get_arg(argsinfo, field, default = None):
    arg = default
    if field in argsinfo:
        arg = argsinfo[field]
    return arg

def get_optional(argsinfo, field, default = None):
    return _get_arg(argsinfo, field, default)

def get_args(argsinfo, field, default=None):
    arg = _get_arg(argsinfo, field, default)
    if arg is None:
        print(field + " is missing in argsinfo!")
        exit()
    return arg


def dprint(module, msg):
    global counter
    print("")
    print("=-=-=-=-=-==============================================-=-=-=-=-=")
    print("=-=-=-=-=-= "+str(counter)+ ". "+module + ": " + msg+ "=-=-=-=-=-=")
    counter = counter + 1

def wait_idrac(idrac, sl=5):
    for i in range(1, 1000):
        print('waiting for ' + str(i))
        time.sleep(sl)
        if idrac.reconnect():
                break
    print('acheived nirvana')


###############################
# Initializing Arguments
###############################

with open("omsdktest\\idrac.info", "r") as enum_data:
    argsinfo = json.load(enum_data)

ipaddr = get_args(argsinfo, 'ipaddr')
driver = get_optional(argsinfo, 'driver')
uname = get_optional(argsinfo, 'user.name')
upass = get_optional(argsinfo, 'user.password', '')
pref = get_optional(argsinfo, 'protocol', 'WSMAN')
nshare = get_optional(argsinfo, 'share')
nsharename = get_optional(argsinfo, 'share.user.name')
nsharepass = get_optional(argsinfo, 'share.user.password', '')
image = get_optional(argsinfo, 'image', '')
creds = ProtocolCredentialsFactory()
if uname :
    creds.add(UserCredentials(uname, upass))
protopref = None
if pref == "WSMAN":
    protopref = ProtoPreference(ProtocolEnum.WSMAN)

@property
def not_implemented():
    print("===== not implemented ====")


if platform.system() == "Windows":
    myshare = FileOnShare(remote =nshare,
        #mount_point='Z:\\', isFolder=True,
        isFolder=True,
        creds = UserCredentials(nsharename, nsharepass))
    updshare = myshare
else:
    myshare = FileOnShare(remote =nshare,
        mount_point='/tst', isFolder=True,
        creds = UserCredentials(nsharename, nsharepass))
    updshare = myshare

sd = sdkinfra()
sd.importPath()

UpdateManager.configure(updshare)
updshare.IsValid
    

t1 = time.time()

RunNow = True
ToTest = False
Passed = False
Failed = False


if True:
    dprint("Driver SDK", "1.03 Connect to " + ipaddr)
    idrac = sd.get_driver(sd.driver_enum.iDRAC, ipaddr, creds, protopref)
    if idrac is None:
        print ("Error: Not found a device driver for: " + ipaddr)
        exit()
    else:
        print("Connected to " + ipaddr)

if Passed:
    idrac.config_mgr.set_liason_share(myshare)
    print(idrac.config_mgr.TimeZone)
    UpdateHelper.save_firmware_inventory(idrac)
    idrac.disconnect()
    UpdateManager.update_catalog()
    UpdateHelper.build_repo()
    UpdateManager.update_cache()

if Passed:
    UpdateHelper.build_repo('BIOS', catalog='BIOS_Catalog')
    UpdateHelper.build_repo(catalog='Model_Catalog', scoped=False)

if Passed:

    print(idrac.config_mgr.enable_snmp(community = 'public', snmp_port=161))
    print(idrac.config_mgr.enable_syslog(syslog_port = 514))
    print(idrac.config_mgr.disable_syslog())
    print(idrac.config_mgr.enable_ntp(ntp_max_dist = 16))

if Passed:
    dprint("Driver SDK", "2.02 Create User")
    retVal = idrac.user_mgr.create_user('vv1', 'vaidees123', UserPrivilegeEnum.Administrator)
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    niso = myshare.new_file(image)
    msg = idrac.config_mgr.boot_to_network_iso(niso)
    print(PrettyPrint.prettify_json(msg))


if Passed:
    print(idrac.config_mgr.BootMode)
    print(idrac.config_mgr.CSIOR)
    print(idrac.config_mgr.SSLEncryptionBits)
    print(idrac.config_mgr.TLSProtocol)
    print(idrac.config_mgr.change_boot_mode(mode = idrac.config_mgr.BootMode))
    print(idrac.config_mgr.configure_tls(tls_protocol = idrac.config_mgr.TLSProtocol))
    print(idrac.config_mgr.SyslogServers)
    print(idrac.config_mgr.SyslogConfig)
    print(idrac.config_mgr.NTPServers)
    print(idrac.config_mgr.NTPEnabled)

if Passed:
    tz = idrac.config_mgr.TimeZone
    print(idrac.config_mgr.configure_time_zone(None))
    print(idrac.config_mgr.TimeZone)
    print(idrac.config_mgr.configure_time_zone(tz))
    print(idrac.config_mgr.TimeZone)
    print(idrac.config_mgr.SNMPTrapDestination)
    print(idrac.config_mgr.SNMPConfiguration)

if Passed:
    print(PrettyPrint.prettify_json(idrac.config_mgr.LCReady))
    print(PrettyPrint.prettify_json(idrac.config_mgr.LCStatus))
    print(PrettyPrint.prettify_json(idrac.config_mgr.ServerStatus))
    print(PrettyPrint.prettify_json(idrac.config_mgr.lc_status()))

if Passed:
    print(PrettyPrint.prettify_json(idrac.job_mgr.delete_job(jobid ="JID_966529634181")))

if Passed:
    print(PrettyPrint.prettify_json(idrac.job_mgr.delete_all_jobs()))

if Passed:
    #print(PrettyPrint.prettify_json(idrac.license_mgr._get_license_json()))
    print("============= LicenseDevice FQDDs ======")
    print(PrettyPrint.prettify_json(idrac.license_mgr.LicensableDeviceFQDDs))
    print("============= LicenseDevice ======")
    print(PrettyPrint.prettify_json(idrac.license_mgr.LicensableDevices))
    print("============= Licenses ======")
    print(PrettyPrint.prettify_json(idrac.license_mgr.Licenses))

if Passed:
    dprint("Driver SDK", "2.01 Server Power On")
    retVal = idrac.config_mgr.change_power(PowerStateEnum.PowerOn)
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "2.01 List Users")
    print(PrettyPrint.prettify_json(idrac.user_mgr.Users))

if Passed:
    dprint("Driver SDK", "2.02 Create User")
    retVal = idrac.user_mgr.create_user('vv1', 'vaidees123', UserPrivilegeEnum.Administrator)
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "2.02 Change User Role")
    retVal = idrac.user_mgr.change_privilege('vv1', UserPrivilegeEnum.Operator)
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "2.02 Change User Password")
    retVal = idrac.user_mgr.change_password('vv1', 'vaidees123', 'newvaidees')
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "2.02 Delete User")
    retVal = idrac.user_mgr.delete_user('vv1')
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "SNMP Trap Destination")
    retVal =idrac.config_mgr.add_trap_destination('omisc.trap.host')
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "5.03 Get System Information")
    idrac.get_entityjson()
    print(PrettyPrint.prettify_json(idrac.get_json_device()))

if RunNow:
    dprint("Driver SDK", "5.04 Export SCP")
    scp_file = myshare.new_file('fact_%ip_%Y%m%d_%H%M%S.xml')
    msg = idrac.config_mgr.scp_export(scp_file, method=ExportMethodEnum.Clone)
    print(PrettyPrint.prettify_json(msg))

    if msg['Status'] == "Success":
        print("Saved to file :" + msg['file'])
    else:
        print("Operation Failed with Message :" + msg['Message'])

if Passed:
    dprint("Driver SDK", "5.04 Export SCP Async")
    scp_file = myshare.new_file('fact_%ip_%Y%m%d_%H%M%S.xml')
    msg = idrac.config_mgr.scp_export(scp_file, job_wait=False)
    print(PrettyPrint.prettify_json(msg))
    if msg['Status'] == 'Success':
        print("Saving to file :" + msg['file'])
        jobid = msg['Job']['JobId']
        retVal = idrac.job_mgr.job_wait(jobid, show_progress=True)
        if msg['Status'] == "Success":
            print("Successfully saved file!")
        else:
            print("Job Failed with Message :" + msg['Message'])
    else:
        print("Operation Failed with Message :" + msg['Message'])

if Passed:
    dprint("Driver SDK", "5.06 Export License")
    print("Licenses exported:")
    print(idrac.license_mgr.export_license(os.path.join(".", "license")))

if Passed:
    dprint("Driver SDK", "5.06 Export License To Share")
    license_file = myshare.new_file('idrac.license')
    msg = idrac.license_mgr.export_license_share(license_file)
    print(PrettyPrint.prettify_json(msg))

if Passed:
    dprint("Driver SDK", "Export TSR")
    tsr_file = myshare.new_file('idrac.tsr.zip')
    retVal = idrac.config_mgr.export_tsr(tsr_file, job_wait = False)
    print(PrettyPrint.prettify_json(retVal))
    if retVal['Status'] == 'Success':
        print("Saved to file :" + retVal['file'])
        jobid = retVal['Job']['JobId']
        retVal = idrac.job_mgr.job_wait(jobid, show_progress=True)
        print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "7.01 OS deployment")
    retVal = idrac.config_mgr.detach_iso_from_vflash()
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.detach_drivers()
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.disconnect_network_iso()
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.detach_iso()
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.DriverPackInfo
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.HostMacInfo
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "5.05 Import SCP")
    scp_file = myshare.new_file('user.xml')
    msg = idrac.config_mgr.scp_import(scp_file)
    print(PrettyPrint.prettify_json(msg))

if Passed:
    dprint("Driver SDK", "5.05 Import SCP Async")
    scp_file = myshare.new_file('user.xml')
    msg = idrac.config_mgr.scp_import(scp_file, job_wait=True)
    print(PrettyPrint.prettify_json(msg))
    if msg['Status'] == 'Success':
        print("Saved to file :" + msg['file'])
        jobid = msg['Job']['JobId']
        retVal = idrac.job_mgr.job_wait(jobid, show_progress=True)
        PrettyPrint.prettify_json(retVal)

#------------------------
if Passed:
    dprint("Driver SDK", "5.06 Import License")
    new_license = os.path.join(".", "license", "lice.txt")
    msg = idrac.license_mgr.import_license(new_license)
    print(PrettyPrint.prettify_json(msg))
    if msg['Status'] == "Success":
        print("Import License Successful!")
    else:
        print("Operation Failed with Message :" + msg['Message'])

if Passed:
    dprint("Driver SDK", "5.01 Update NIC Configuration")
    retVal = idrac.config_mgr.configure_tls(tls_protocol='TLS 1.1 and Higher')
    print(PrettyPrint.prettify_json(retVal))
    wait_idrac(idrac)


if False:
    print(idrac.config_mgr.create_raid('VD0', 1, 1, idrac.eRAIDLevelsEnum.RAID_0, 0))
    #print(idrac.config_mgr.delete_raid('Virtual Disk 1'))
    #print(PrettyPrint.prettify_json(idrac.update_mgr.InstalledFirmware))

if Passed:
    dprint("Driver SDK", "4.01.1 download catalog.xml.gz from ftp.dell.com")
    print(UpdateManager.update_catalog())
    dprint("Driver SDK", "4.01.2 build cache using idracs/models")
    print(UpdateManager.add_devices(idrac))
    dprint("Driver SDK", "4.01.3 Refresh the existing localstore")
    print(UpdateManager.update_cache())

if Passed:
    dprint("Driver SDK", "4.01 Firmware Inventory")
    invcol_file = os.path.join(".", "output", "inv.xml")
    idrac.update_mgr.save_invcollector_file(invcol_file)
    print("Saved to " + invcol_file)

if Passed:
    dprint("Driver SDK", "4.01 Prepare new Catalog (ftp.dell.com) on par with device")
    catalog = idrac.update_mgr.catalog_scoped_to_device()
    print(catalog.cache_share.local_full_path)
    #catalog.dispose()

if Passed:
    dprint("Driver SDK", "4.01 Prepare new Catalog (ftp.dell.com) for the entire model")
    catalog = idrac.update_mgr.catalog_scoped_to_model()
    print(catalog.cache_share.local_full_path)
    #catalog.dispose()

if Passed:
    dprint("Driver SDK", "4.01 Prepare new Catalog (ftp.dell.com) for component")
    catalog = idrac.update_mgr.catalog_scoped_to_components('iDRAC','NIC')
    print(catalog.cache_share.local_full_path)
    #catalog.dispose()

if Passed:
    dprint("Driver SDK", "3.01 Update BIOS (ftp.dell.com) for BIOS")
    catalog = idrac.update_mgr.catalog_scoped_to_components('BIOS')
    print(catalog.cache_share.local_full_path)
    #catalog.dispose()

if Passed:
    dprint("Driver SDK", "4.01 Prepare new Catalog (ftp.dell.com) for component")
    catalog = idrac.update_mgr.catalog_scoped_to_components('Controller','Enclosure', 'PhysicalDisk')
    print(catalog.cache_share.local_full_path)
    #catalog.dispose()
if Passed:
    dprint("Driver SDK", "5.06 Import License From Share")
    license_file = myshare.new_file('idrac.license')
    msg = idrac.license_mgr.import_license_share(license_file)
    print(PrettyPrint.prettify_json(msg))

if Passed:
    dprint("Driver SDK", "5.06 Replace License")
    new_license = os.path.join(".", "license", "lice.txt")
    msg = idrac.license_mgr.replace_license(new_license, "FD00000004931048")
    print(PrettyPrint.prettify_json(msg))

if Passed:
    dprint("Driver SDK", "5.06 Delete License")
    msg = idrac.license_mgr.delete_license("FD00000004931048")
    print(PrettyPrint.prettify_json(msg))

if Passed:
    dprint("Driver SDK", "5.02 Update iDRAC Configuration")
    retVal = idrac.config_mgr.configure_idrac_nic(idrac_nic='Dedicated')
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.configure_idrac_dnsname(dnsname = "idrac.dns.name")
    print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.configure_idrac_ipv4(enable_ipv4=True, dhcp_enabled=True)
    print(PrettyPrint.prettify_json(retVal))
    #retVal = idrac.config_mgr.configure_idrac_ipv4static(idrac.ipaddr,
    #            netmask = "255.255.255.0", gateway="192.168.0.1",
    #            dnsarray=["1.0.0.1"], dnsFromDHCP=False)
    #print(PrettyPrint.prettify_json(retVal))
    retVal = idrac.config_mgr.disable_idracnic_vlan()


if Passed:
    dprint("Driver SDK", "6.01 RAID Configuration")
    span_length = 1
    span_depth = 2
    raid_type = "RAID 5"
    idrac.config_mgr.create_raid("My VD0", span_length, span_depth,raid_type,4)

if Passed:
    dprint("Driver SDK", "2.01 Server Power Off")
    # Turns off Server Power
    retVal = idrac.config_mgr.change_power(idrac.ePowerStateEnum.SoftPowerOff)
    print(PrettyPrint.prettify_json(retVal))

if Failed:
    # not working!!
    dprint("Driver SDK", "2.01 Server Power Cycle")
    retVal = idrac.config_mgr.change_power(idrac.ePowerStateEnum.PowerCycle)
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "2.01 Server Hard Reset")
    retVal = idrac.config_mgr.change_power(idrac.ePowerStateEnum.HardReset)
    print(PrettyPrint.prettify_json(retVal))

if Passed:
    dprint("Driver SDK", "2.01 iDRAC Reset")
    retVal = idrac.config_mgr.reset_idrac(force=idrac.eResetForceEnum.Graceful)
    print(PrettyPrint.prettify_json(retVal))

if ToTest:
    dprint("Driver SDK", "2.01 Reset to Factory Defaults")
    retVal = idrac.config_mgr.reset_to_factory()
    print(PrettyPrint.prettify_json(retVal))

if ToTest:
    dprint("Driver SDK", "3.02 Update Boot Order Configuration")
    not_implemented

if ToTest:
    dprint("Driver SDK", "3.02 Change Boot Mode")
    not_implemented

if ToTest:
    dprint("Driver SDK", "4.01 Update Firmware using DRM Repo")

if idrac:
    idrac.reset()

print("Executed for {0} seconds".format(time.time()-t1))
#retVal = idrac.config_mgr.change_power(idrac.ePowerStateEnum.GracefulPowerOff)
