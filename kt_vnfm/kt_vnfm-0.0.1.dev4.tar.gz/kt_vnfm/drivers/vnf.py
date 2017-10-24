#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from pyasn1.type import namedval

import os, sys, time, shutil
from kt_vnfm.drivers.vnf_states import VNFState

import traceback
import threading
import pyping

from kt_vnfm.connector.vmconnector_restapi import vmconnector_restapi
from kt_vnfm.connector.vmconnector_ssh import vmconnector_ssh

from kt_vnfm.utils import auxiliary_functions as af

import kt_vnfm.utils.log_manager as log_manager
logger = log_manager.LogManager.get_instance()

class VNF:    
    __metaclass__ = ABCMeta
    
    ####################### ABSTRACT METHODS #######################
    @abstractmethod
    def backup(self, repo, params):
        pass
    
    @abstractmethod
    def restore(self, repo, params):
        pass
    
    @abstractmethod
    def is_online(self):
        pass 
    
    ######################## BASIC METHODS ##########################
    # TODO: start/stop/restart method should be abstract
    def start(self):
        pass

    def stop(self):
        pass
    
    def restart(self):
        pass
    
    def update_status(self, max_count, need_resume_wan_monitor=False):
        count = 0
        
        logger.debug("[VNF.update_status] thread started")
        while True:
            logger.debug("[VNF.update_status] thread Running, %d " % count)
            try:
                if count > max_count:                
                    logger.debug("[VNF.update_status] thread reached its maximum count, %d " % max_count)
                    self.set_status(VNFState.UNDEFINED)
                    break
                            
                cur_status = self.get_status()
                if self.is_online():               
                    if cur_status == VNFState.RESTARTING:
                        logger.debug("[VNF.update_status] VNFState changed from %s to %s " % (VNFState.RESTARTING.name, VNFState.RUNNING.name))
                        self.set_status(VNFState.RUNNING)
                        
                        if need_resume_wan_monitor == True:
                            logger.debug("[VNF.update_status] after 40 sec. resume WAN-Monitoring of One-Box Agent")
                            time.sleep(40)
                            logger.debug("[VNF.update_status] resume WAN-Monitoring of One-Box Agent")
                            oba_conn = oba_connector()
                            oba_result, oba_data = oba_conn.resume_monitor_wan()
                            logger.debug("[VNF.update_status] Result of resuming wan monitor: %s %s" %(str(oba_result), str(oba_data)))
                        else:
                            logger.debug("[HJC][VNF.update_status] do not need to resume WAN-Monitoring of One-Box Agent")      
                
                        break
                else:
                    if cur_status == VNFState.RESTART_REQUESTED:
                        logger.debug("[VNF.update_status] VNFState changed from %s to %s " % (VNFState.RESTART_REQUESTED.name, VNFState.RESTARTING.name))
                        self.set_status(VNFState.RESTARTING)
                    
                count = count + 1                   
                time.sleep(3)
            except Exception, e:
                logger.exception("Exception: %s" %str(e))
                self.set_status(VNFState.UNDEFINED)
                
        logger.debug("[VNF.update_status] thread done.")

    def insert_ssh_key(self, vm_conn=None, path='/root/.ssh/id_rsa.pub'):
        if vm_conn is None:
            vm_conn = self.get_vnf_conn()
        
        if vm_conn is None:
            return -500, "No Connection to VNF VM"
        
        options = '-oStrictHostKeyChecking=no'
        
        if vm_conn.host.find("192.168.254.") >= 0: #vm_conn.action == "UPDATE":
            mkdir_cmd = "ssh %s %s@%s mkdir .ssh" % (options, vm_conn.user, vm_conn.host)
            result1, content1 = vm_conn.exec_pexpect(mkdir_cmd)
            
            scp_cmd = "scp %s %s %s@%s:.ssh/authorized_keys" % (options, path, vm_conn.user, vm_conn.host)
            logger.debug('command: %s' % scp_cmd)
            
            result, content = vm_conn.exec_pexpect(scp_cmd)
        else:
            mkdir_cmd = "ip netns exec %s ssh %s %s@%s mkdir .ssh" % (vm_conn.net_ns, options, vm_conn.user, vm_conn.host)
            result1, content1 = vm_conn.exec_pexpect(mkdir_cmd)
            
            scp_cmd = "ip netns exec %s scp %s %s %s@%s:.ssh/authorized_keys" % (vm_conn.net_ns, options, path, vm_conn.user, vm_conn.host)
            logger.debug('command: %s' % scp_cmd)
            
            result, content = vm_conn.exec_pexpect(scp_cmd)
        
        return result, content
    
    def copy_config_script_files(self):
        vm_conn = self.get_vnf_conn()
        if vm_conn is NOne:
            return -500, "No Connection to VNF VM"
        
        path = '/var/onebox/vnf_configs/' + str(self.get_name())      
        logger.debug("config builtin script path: %s" %path)
        
        if os.path.exists(path) and os.path.isdir(path):
            result, content = vm_conn.copy_directory(path) # or for-loop copy_file()
            if result < 0:
                logger.error ("failed to copy config script files into VNF VM: %s" %path)
                return -500, "failed to copy config script files into VNF VM: %s" %path
        else:
            return -500, "No Directory for VNF Config Scripts"
        
        return 200, "OK"
    
    def need_wan_switch(self, request_value, action=None):
        return request_value
    
    def run_config_script(self, script, action=None):
        ret_output={}
        try:
            vm_conn = self.get_vnf_conn()
            if vm_conn is None:
                raise Exception("Failed to get VNF VM Connection")
        
            result, content = vm_conn.do_script(script)
                
            if result > 0:
                #logger.debug("Type of content: %s" %str(type(content)))
                if type(content) is dict and content.get('success') is not None:
                    #logger.debug("success type, value: %s, %s" %(str(type(content.get('success'))), str(content.get('success'))))
                    if content.get('success', False) is True:
                        logger.debug("Step 3. Command : response success is True: %s" %str(content))
                        result = 200
                    else:
                        logger.debug("Step 3. Command : response success is False: %s" %str(content))
                        result = -500
                
                logger.debug("Step 3. Command : Final Result Value = %s" %str(result))
                if result < 0:    
                    logger.error("Failed to do: %s" %(str(script)))
                    raise Exception("Failed to do: %s" %(str(script)))
            
            output_list = script.get("output")
            if output_list:
                #logger.debug("[HJC] output: %s" %str(output_list))
                for output in output_list:
                    if output == "local_ip":
                        vm_local_ip = str(content)
                        ret_output['local_ip'] = vm_local_ip
                        #logger.debug("[HJC] VM Local IP = %s" %str(vm_local_ip))                        
                    
                    if output == "public_ip":
                        vm_public_ip = str(content)
                        ret_output['public_ip'] = vm_public_ip
                        #logger.debug("[HJC] VM Public IP = %s" %str(vm_public_ip))
            
            return 200, ret_output
        except Exception, e:
            err_msg = "Script Exception [%s] %s" % (str(e), sys.exc_info())
            logger.exception(err_msg)            
            return -500, err_msg
        
    def get_vmconnector(self, mgmt_ip=None, user_name='root', password='qazwsx123', type='ssh', action_type='INIT'):
        '''Obtain an instance of VM Connector 
        '''
        logger.debug("[HJC] IN")
        if mgmt_ip is None:
            if self.get_mgmt_ip() is not None:
                mgmt_ip = self.get_mgmt_ip()
            else:
                mgmt_ip = self.get_local_mgmt_ip()

        if type == 'ssh':
            vm_conn = vmconnector_ssh(
                            name=self.name, host=mgmt_ip, uuid=self.uuid, 
                            user=user_name, passwd=password, action=action_type
                            )
        elif type == 'rest_api':
            vm_conn = vmconnector_restapi(
                            name=self.name, host=mgmt_ip, uuid=self.uuid,
                            user=user_name, passwd=password, action=action_type
                            )
            
        logger.debug("[HJC] OUT")
        return vm_conn

    ######################## GETTER/SETTER METHODS ##########################
    def set_name(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def set_uuid(self, vm_uuid):
        self.uuid = vm_uuid
        
    def get_uuid(self):
        return self.uuid
        
    def set_status(self, status):
        self.status = status
        
    def get_status(self):
        return self.status
    
    def set_vnf_driver(self, vnf_driver):
        self.vnf_driver = vnf_driver    
    
    def get_vnf_driver(self):
        return self.vnf_driver
    
    def set_local_mgmt_ip(self, local_mgmt_ip):
        self.local_mgmt_ip = local_mgmt_ip    
    
    def get_local_mgmt_ip(self):
        return self.local_mgmt_ip
    
    def set_mgmt_ip(self, mgmt_ip):
        self.mgmt_ip = mgmt_ip
        
    def get_mgmt_ip(self):
        return self.mgmt_ip
    
    def set_public_ip(self, public_ip):
        self.public_ip = public_ip
        
    def get_public_ip(self):
        return self.public_ip
    
    def set_user(self, user_id):
        self.user = user_id
        
    def get_user(self):
        return self.user
    
    def set_password(self, user_password):
        self.password = user_password
        
    def get_password(self):
        return self.password
    
    def set_vnf_conn(self, vm_conn):
        self.vnf_conn = vm_conn
    
    def get_vnf_conn(self):
        return self.vnf_conn
        

class VNF_SSH(VNF):
    instances = {}
    
    # pass an instance of a vnf driver (e.g., EndianUTM_Driver())
    def __init__(self, name, local_mgmt_ip, vnf_driver):        
        self.set_name(name)
        self.set_local_mgmt_ip(local_mgmt_ip)
        self.set_vnf_driver(vnf_driver)
        # TODO: to be updated - should be stop at initial state, and there should be a method that update its status to running 
        self.set_status(VNFState.RUNNING)
    
    def execute_vnf_backup(self):
        backup_filename = ""
        try:
            conn_local = ssh_connector(self.get_local_mgmt_ip())
            
            command = self.get_vnf_driver().cmd_backup()    
            result, output = conn_local.run_ssh_command(command)    
            
            if output != None and len(output) > 0:
                backup_file = output[0]
            
            # TODO: copy backup file in the VNF to local storage
            result, output = conn_local.run_scp_command(backup_file)    
            backup_filename=output 
        
            logger.debug("[VNF_SSH: execute_vnf_backup OK] output= %s" % output)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            
        return backup_filename    
    
    def execute_vnf_restore(self, backup_filename):
        try:
            conn_local = ssh_connector(self.get_local_mgmt_ip())            
            command = self.get_vnf_driver().cmd_restore(backup_filename)    
            
            logger.debug("[VNF_SSH: execute_vnf_restore CALL] command= %s" % command)
            result, output = conn_local.run_ssh_command(command)
            
            if result < 0:
                return -500
            # Update VNFState and run status check thread
            logger.debug("[VNF_SSH: execute_vnf_restore] Update VNF State to %s " % VNFState.RESTART_REQUESTED.name)
            self.set_status(VNFState.RESTART_REQUESTED)
            check_thread = threading.Thread(target=self.update_status, args=(120,))
            check_thread.start()  
            logger.debug("[VNF_SSH: execute_vnf_restore] Current VNF State %s " % self.get_status().name)
            logger.debug("[VNF_SSH: execute_vnf_restore OK] output= %s" % output)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            return -500
        
        return 200
            
    def copy_from_remote_storage(self, backup_server_ip, backup_file):
        # TODO: Copy backup file from remote storage (backup server)
        try:    
            conn_remote = ssh_connector(backup_server_ip, 9922)
            
            # TODO: Copy backup file from remote storage to local storage
            backup_filename=os.path.basename(backup_file)
            result, output = conn_remote.run_scp_command(backup_file)
            logger.debug("[VNF_SSH: copy_from_remote_storage OK] output= %s" % output)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
             
        return backup_filename                   
    
    def copy_to_remote_storage(self, backup_server_ip, remote_storage, backup_filename):
        # Copy backup file to remote storage (backup server)
        # create remote storage if not exists
        try:    
            conn_remote = ssh_connector(backup_server_ip, 9922)
            
            command = {}
            command["name"]= "mkdir"
            command["params"] = [ "-p", remote_storage ]
            
            #logger.debug("command= %s" % (command))
            result, output = conn_remote.run_ssh_command(command)
            #logger.debug("command= %s output= %s" % (command, output))    
            
            # Copy backup file to local storage
            result, output = conn_remote.run_scp_command(backup_filename, remote_storage, method="PUT")
            if result < 0:
                logger.error("[VNF_SSH: copy_to_remote_storage NOK] Failed to remote-copy VNF backup file")
                return result, "Failed to remote-copy VNF backup file"
            else:
                logger.debug("[VNF_SSH: copy_to_remote_storage OK] output= %s" % output)            
                return 200, str(output)
        except Exception, e:
            logger.exception("Exception: %s" %str(e))
            return -500, str(e)
            
    def copy_to_local_storage(self, local_storage, backup_filename):
         # TODO: Run backup script and get backup file name
        try:
            if not os.path.exists(local_storage):
                os.makedirs(local_storage)
                shutil.copy(backup_filename, local_storage)
            else:
                shutil.copy(backup_filename, local_storage)
        
            if os.path.isfile(backup_filename): 
                os.remove(backup_filename)
                
            logger.debug("[VNF_SSH: copy_to_local_storage OK] output= %s" % backup_filename)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            
        return backup_filename
    
    def upload_vnf_backup(self, backup_file):
        backup_filename = ""
        try:
            conn_local = ssh_connector(self.get_local_mgmt_ip())
            
            # TODO: copy backup file in the VNF to local storage     
            backup_filename=os.path.basename(backup_file)   
            remote_file_location="/root/%s" % backup_filename
            result, output = conn_local.run_scp_command(backup_file, remote_file_location, method="PUT")
                
            logger.debug("[VNF_SSH: upload_vnf_backup OK] local_mgmt_ip= %s local file= %s remote_file_location= %s" % (self.get_local_mgmt_ip(), backup_file, remote_file_location))
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            
        return backup_filename   
        
    def backup(self, repo, params):
        msg = None
        local_storage   = repo.local_backup_storage(self.get_name())   
        remote_storage  = repo.remote_backup_storage(self.get_name())
        
        backup_server_ip = params['backup_server_ip']
                     
        backup_filename = self.execute_vnf_backup()
        
        if backup_filename is None or backup_filename == "":
            return None, None
        
        self.copy_to_local_storage(local_storage, backup_filename)
        local_location="%s/%s" % (local_storage, backup_filename)
        
        if params.get('backup_type', "default").find("local") >= 0:
            remote_location = None
            msg = "Backup Type is %s" %params.get('backup_type', "default")
            logger.debug("[HJC] %s" %msg)
        else:
            #r_result, r_data = self.copy_to_remote_storage(backup_server_ip, remote_storage, backup_filename)
            r_result, r_data = self.copy_to_remote_storage(backup_server_ip, remote_storage, local_location)
            if r_result < 0:
                remote_location=None
                msg = str(r_data)
            else:
                remote_location="%s/%s" % (remote_storage, backup_filename)
        
        return local_location, remote_location, msg
        
    def restore(self, repo, params, force=True):
        local_storage   = repo.local_backup_storage(self.get_name())   
        remote_storage  = repo.remote_backup_storage(self.get_name())
        
        backup_server_ip = params['backup_server_ip']
        local_location = params['local_location']
        remote_location = params['remote_location']                     
       
        # TODO: Exception handling and return error codes
        # TODO: check if backup file exists in local repository
        if os.path.exists(local_location):
            # TODO: if backup file exist, copy the file to UTM and run restore command
            backup_filename=self.upload_vnf_backup(local_location)
            result = self.execute_vnf_restore(backup_filename)
            
            if result < 0:
                msg = "failed to restore vnf using local backup"
                status = "NOK"
            else:
                msg = "request vnf restore using local backup"
                status = "OK"
        else:
            # TODO: if backup file does not exist in local repository, check if the backup file exist in remote repository
            # TODO: copy the backup file from remote repository to local directory
            backup_filename=self.copy_from_remote_storage(backup_server_ip, remote_location)
            # TODO: copy the file to UTM and run restore command    
            backup_filename=self.upload_vnf_backup(backup_filename)
            result = self.execute_vnf_restore(backup_filename)
            if result < 0:
                msg = "failed to restore vnf using remote backup"
                status = "NOK"
            else:
                msg = "request vnf restore using remote backup"
                status = "OK"
        
        return status, msg
    
    def is_online(self):
        response = pyping.ping(self.get_local_mgmt_ip())    
        if response.ret_code == 0: # can connect                
            return True
        else: # cannot connect
            return False
