# -*- coding: utf-8 -*-

import os, sys, time
from optparse import OptionParser
from kt_vnfm.drivers.axgate_utm import AXGATE_UTM

def main():
    usage = "usage: %prog [options] ip-address port"
    version = "AxGate VPN VNF manager version 0.0.1 (c) Copyright KT"
    
    vnf_dict = {}
    vnf_dict['name'] = "vpnns-XXp8s2Q25-evpnvnfdVM"
    vnf_dict['uuid'] = "71347f1a-39d5-418e-bce5-f4965aaca565"
    vnf_dict['mgmtip'] = "10.0.10.12"
    vnf_dict['local_ip'] = "10.0.10.12"
    vnf_dict['user'] = "axroot"
    vnf_dict['password'] = "Admin12#$"
    
    print "vnf_dict= %s" % vnf_dict
    
    local_mgmt_ip = "10.0.10.12"
    instance = AXGATE_UTM.get_instance(vnf_dict)
    result, content = instance.setup_connection()
    
    sessionid = content['SessionID']
    print "sessionid = %s" % sessionid
    
    sw_version = instance.get_sw_version(sessionid)
    print "sw_version = %s" % sw_version['content']
    
    content = instance.set_network_interface(sessionid, ["eth1", "192.168.0.1", 24, "uplink_main"])
    print "content= %s" % content['content']
    
if __name__=="__main__":
    main()
