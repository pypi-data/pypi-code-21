##
# kt GiGA One-Box Orchestrator version 1.0
#
# Copyright 2016 kt corp. All right reserved
#
# This is a proprietary software of kt corp, and you may not use this file
# except in compliance with license agreement with kt corp.
#
# Any redistribution or use of this software, with or without modification
# shall be strictly prohibited without prior written approval of kt corp,
# and the copyright notice above does not evidence any actual or intended
# publication of such software.
##

'''
vmconnector_ssh implements all the methods to connect to VMs through ssh.
'''
__author__="Jechan Han"
__date__ ="$15-oct-2015 17:44:29$"

import requests
import sys
from kt_vnfm.utils import auxiliary_functions as af

from httplib import HTTPException
import time 
import commands
import pexpect 

import kt_vnfm.utils.log_manager as log_manager
logger = log_manager.LogManager.get_instance()

class vmconnector_ssh():
    def __init__(self, name, host, uuid=None, user=None, passwd=None, url=None, debug=True, config={}, action="INIT"):
        '''using common constructor parameters. In this case 
        'url' is the ip address or ip address:port,
        ''' 
 
        self.id        = uuid
        self.name      = name
        self.host = host
        if not host:
            raise TypeError, 'host param can not be NoneType'
        self.url       = url
        self.user      = user
        self.passwd    = passwd
        self.config              = config
        self.action    = action
        self.debug               = debug
        self.reload_client       = True
        self.reload_network_namespace()        
    
    def __getitem__(self,index):
        if index=='id':
            return self.id
        elif index=='name':
            return self.name
        elif index=='user':
            return self.user
        elif index=='passwd':
            return self.passwd
        elif index=='host':
            return self.host
        elif index=='url':
            return self.url
        elif index=='config':
            return self.config
        elif index=='action':
            return self.action
        elif index=='net_ns':
            return self.net_ns
        else:
            raise KeyError("Invalid key '%s'" %str(index))
        
    def __setitem__(self,index, value):
        '''Set individuals parameters 
        '''
        if index=='id':
            self.id = value
        elif index=='name':
            self.name = value
        elif index=='user':
            self.reload_client=True
            self.user = value
        elif index=='passwd':
            self.reload_client=True
            self.passwd = value
        elif index=='host':
            self.reload_client=True
            self.host=value
        elif index=='url':
            self.reload_client=True
            self.url = value
            if value is None:
                raise TypeError, 'url param can not be NoneType'
        elif index=='action':
            self.action = value
        elif index=='net_ns':
            self.net_ns = value
        else:
            raise KeyError("Invalid key '%s'" %str(index))

    def reload_network_namespace(self):
        try:
            result, content = commands.getstatusoutput("ip netns | grep qrouter")
        except:
            result = -500
            
        if result == 0:
            self.net_ns = content
        else:
            logger.error("failed to get the network namespace of the HOST")
            self.net_ns = None
        
        return 

    #expect_dict: expect_key, expect_reaction_function_name
    def exec_pexpect(self, cmd, timeout_=60, expect_dict={}):
        result = 200
        content = "None"
        
        try:
            logger.debug("do command %s" %cmd)
            child = pexpect.spawn(cmd, timeout=timeout_)
            #child.logfile = sys.stdout
            
            resp = child.expect(['password: ', pexpect.EOF, 'No route to host', 'Connection refused'])
            
            if resp == 0:
                logger.debug('send password %s' % self.passwd)
                child.sendline(self.passwd)
                
                resp = child.expect(['Permission denied', pexpect.EOF])
                if resp == 0:
                    result = -401
                    content = "Permission denied on host. Cannot login"
                    logger.error(content)
                    child.kill(0)
                elif resp == 1:
                    logger.debug("Success to login with the password: %s" %self.passwd)
                    content = child.before
            elif resp == 1:
                content = str(child.before)
                logger.debug("Success to do the command: %s" %content)
                
                if content.find("Connection refused") >= 0:
                    logger.debug("exec result: Connection refused")
                    result = -503
            elif resp == 2:
                result = -503
                content = child.before
                logger.debug(content)
            elif resp == 3:
                result = -503
                content = "Wait for completion of VM booting"
                logger.debug(content)
            else:
                result = -500
                content = "Unknown Result"
                logger.debug(content)          
           
            logger.debug('result: %s' %content)
        except pexpect.TIMEOUT:
            result = -500
            content = 'failed to check the connection to %s. Timeout occurred' %self.host
            logger.error(content)
        finally:
            child.close()
        
        return result, content
    
    def check_connection(self, script={}, vnf_local_ip=None):
        if self.host == None:
            return -400, "No Host Info"
        
        if script and len(script) > 0:
            #TODO: use the script to check the connection to VNF VM
            pass
        
        try:
            ssh_cmd = 'ssh-keygen -f \"/root/.ssh/known_hosts\" -R %s' %(self.host)
            logger.debug('command: %s' %ssh_cmd)
            
            r, c = self.exec_pexpect(ssh_cmd)
        except:
            error_msg = "failed to ssh-keygen -f for %s" %(self.host)
            
        try:
            if vnf_local_ip:
                ssh_cmd = 'ssh-keygen -f \"/root/.ssh/known_hosts\" -R %s' %(vnf_local_ip)
                logger.debug('command: %s' %ssh_cmd)
                
                r, c = self.exec_pexpect(ssh_cmd)
        except:
            error_msg = "failed to ssh-keygen -f for %s" %(self.host)
        
        try: 
            options = '-oStrictHostKeyChecking=no'
            #options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
            cmd = 'ls'
            if self.action == "UPDATE":
                ssh_cmd = "ssh %s@%s %s %s" % (self.user, self.host, options, cmd)
            else:
                ssh_cmd = "ip netns exec %s ssh %s@%s %s %s" % (self.net_ns, self.user, self.host, options, cmd)
            logger.debug('command: %s' % ssh_cmd)
            
            trial_no = 1
            while trial_no < 25:
                logger.debug("Trial %d to connect to the VNF VM" % (trial_no))
                
                if trial_no > 1:
                    time.sleep(20)
                
                result, content = self.exec_pexpect(ssh_cmd)
                logger.debug("Result: %s, %s" %(str(result), str(content)))
                if result >= 0:
                    break
                if result == -400 or result == -401:
                    break
                
                trial_no += 1
        except:
            error_msg = "failed to check connection for the VM %s %s" %(self.name, self.host) 
            logger.error(error_msg)
            return -503, error_msg
        
        return result, content

    def do_command(self, cmd, timeout=60):
        try:
            result, content = self.exec_pexpect(cmd, timeout)
        except:
            logger.error("failed to do command %s: %d, %s" %(str(cmd), result, str(content)))
            result = -500

        return result, content
    
    def do_script(self, script):
        try:
            script_name = script['name']
            param_list = script['params']
            
            options = '-oStrictHostKeyChecking=no'
            
            if param_list != None and len(param_list) > 0:
                params = " ".join(param_list)
            else:
                params = ""
            
            if self.action == "UPDATE":
                ssh_cmd = "ssh %s %s@%s %s %s" % (options, self.user, self.host, script_name, params)
            else:
                ssh_cmd = "ip netns exec %s ssh %s %s@%s %s %s" % (self.net_ns, options, self.user, self.host, script_name, params)
            logger.debug('command: %s' % ssh_cmd)
        except:
            error_msg = "failed to compose a command (ssh type) %s" %str(script) 
            logger.error(error_msg)
            return -500, error_msg
        
        result, content = self.exec_pexpect(ssh_cmd)
        
        return result, content
    
    def copy_ssh_key(self, path='/root/.ssh/id_rsa.pub'):
        options = '-oStrictHostKeyChecking=no'
        
        if self.action == "UPDATE":
            scp_cmd = "scp %s %s %s@%s:.ssh/authorized_keys" % (options, path, self.user, self.host)
        else:
            scp_cmd = "ip netns exec %s scp %s %s %s@%s:.ssh/authorized_keys" % (self.net_ns, options, path, self.user, self.host)
        logger.debug('command: %s' % scp_cmd)
        
        result, content = self.exec_pexpect(scp_cmd)
        
        return result, content
    
    def copy_directory(self, path):
        options = '-r -oStrictHostKeyChecking=no'
        
        if self.action == "UPDATE":
            scp_cmd = "scp %s %s %s@%s:" % (options, path, self.user, self.host)
        else:
            scp_cmd = "ip netns exec %s scp %s %s %s@%s:" % (self.net_ns, options, path, self.user, self.host)
        logger.debug('command: %s' % scp_cmd)
        
        result, content = self.exec_pexpect(scp_cmd)
        
        return result, content
    
    def copy_file(self, path):
        options = '-oStrictHostKeyChecking=no'
        
        if self.action == "UPDATE":
            scp_cmd = "scp %s %s %s@%s:" % (options, path, self.user, self.host)
        else:
            scp_cmd = "ip netns exec %s scp %s %s %s@%s:" % (self.net_ns, options, path, self.user, self.host)
        logger.debug('command: %s' % scp_cmd)
        
        result, content = self.exec_pexpect(scp_cmd)
        
        return result, content
