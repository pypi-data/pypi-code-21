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

import os, sys, time, shutil
import traceback
import pyping
import threading
import requests
import json
import datetime, random

from httplib import HTTPException
from requests.exceptions import ConnectionError

from kt_vnfm.drivers.vnf import VNF
from kt_vnfm.drivers.vnf_states import VNFState

import kt_vnfm.connector.vmconnector_restapi as vmconnector_restapi
import kt_vnfm.connector.vmconnector_ssh as vmconnector_ssh

from kt_vnfm.utils import auxiliary_functions as af

import kt_vnfm.utils.log_manager as log_manager
logger = log_manager.LogManager.get_instance()

class AXGATE_SCRIPT:
    REQ_URL = "https;POST;/restrict/exec.cgi"
    REQ_HDR = "Content-type:application/x-www-form-urlencoded;charset=utf-8"
    
    def __init__(self, sessionid):
        self.sessionid = sessionid
        
    def get_sw_version(self):
        script = {}
        
        script['type'] = "rest_api"
        script['name'] = "sw_version"
        script['requesturl'] = self.REQ_URL
        script['requestheaders'] = self.REQ_HDR 
        script['cookieformat'] = 'SessionID=%s'
        script['cookiedata'] = [self.sessionid]
        script['requestheaders_args'] = []
        
        script['body'] = "cmd=show version"
        script['body_args'] = []
        
        script['output'] = []
                
        return script
        
    def set_network_interface(self, args):
        script = {}
        
        script['type'] = "rest_api"
        script['name'] = "set_network_interface"
        script['requesturl'] = self.REQ_URL
        script['requestheaders'] = self.REQ_HDR 
        script['cookieformat'] = 'SessionID=%s'
        script['cookiedata'] = [self.sessionid]
        script['requestheaders_args'] = []
        
        script['body'] = "cmd=configure terminal\\ninterface %s\\nip address %s/%d\\nsecurity-zone %s\\nno shutdown\\nend"
        script['body_args'] = args
        
        script['output'] = []
                
        return script
    
    def set_network_interface_dhcp(self, args):
        script = {}
        
        script['type'] = "rest_api"
        script['name'] = "set_network_interface"
        script['requesturl'] = self.REQ_URL
        script['requestheaders'] = self.REQ_HDR 
        script['cookieformat'] = 'SessionID=%s'
        script['cookiedata'] = [self.sessionid]
        script['requestheaders_args'] = []
        
        script['body'] = "cmd=configure terminal\\ninterface %s\\nip address dhcp\\nsecurity-zone %s\\nno shutdown\\nend"
        script['body_args'] = args
        
        script['output'] = []
                
        return script
    
    def create_ha_cluster(self, args):
        script = {}
        
        script['type'] = "rest_api"
        script['name'] = "create_ha_cluster"
        script['requesturl'] = self.REQ_URL
        script['requestheaders'] = self.REQ_HDR 
        script['cookieformat'] = 'SessionID=%s'
        script['cookiedata'] = [self.sessionid]
        script['requestheaders_args'] = []
        
        script['body'] = "cmd=configure terminal\\nha cluster %d\\nip %s port %d %s direct\\nrouter virtual-ip %d %s/%d %s\\nrouter virtual-ip %d %s/%d %s\\npreempt-mode true\\npriority %d\\nend"
        script['body_args'] = args
        
        script['output'] = []
                
        return script
        
class AXGATE_BASE(VNF):
    
    def backup(self, repo, params):
        raise NotImplementedError
    
    def restore(self, repo, params):
        raise NotImplementedError
    
    def establish_api_session(self, req_dict=None):
        logger.debug("[HJC] establish_api_session: %s" %(str(self.get_local_mgmt_ip())))
        
        headers_req = {'Accept': 'application/json', 'content-type': 'application/json'}
        
        # Step 1. Open a session
        logger.debug("[HJC] 1. open a session: %s" %(str(self.get_local_mgmt_ip())))
        
        URLrequest = "https://" + str(self.get_local_mgmt_ip()) + "/index.dao"
        logger.debug("Request URL: %s" %URLrequest)
        
        try:
            response = requests.post(URLrequest, headers = headers_req)
        except (HTTPException, ConnectionError), e:
            logger.exception("failed to open a session due to HTTP Error %s" %str(e))
            return -500, str(e)
        
        s_result, s_data = self._parse_json_response(ob_response)
        if s_result < 0:
            logger.error("Response: Failed %d, %s" %(s_result, s_data))
            return s_result, s_data
        
        # Step 2. Auth
        logger.debug("[HJC] 2. login : %s" %(str(self.get_local_mgmt_ip())))
        
        URLrequest = "https://" + str(self.get_local_mgmt_ip()) + "/login.dao?username=oadmin&passwd=#2kdnjsqkrtm&force=1"
        logger.debug("Request URL: %s" %URLrequest)
        
        try:
            response = requests.post(URLrequest, headers = headers_req)
        except (HTTPException, ConnectionError), e:
            logger.exception("failed to login due to HTTP Error %s" %str(e))
            return -500, str(e)
        
        s_result, s_data = self._parse_json_response(ob_response)
        if s_result < 0:
            logger.error("Response: Failed %d, %s" %(s_result, s_data))        
        
        return 200, "OK"
    
    def run_config_script(self, script, action=None):
        ret_output={}
        try:
            result, content = self.do_script(script, "4433")
                
            if result > 0:
                pass

                if result < 0:    
                    logger.error("Failed to do: %s" %(str(script)))
                    raise Exception("Failed to do: %s" %(str(script)))
            
            output_list = script.get("output")
            if output_list:
                logger.debug("[HJC] output: %s" %str(output_list))
                for output in output_list:
                    if output == "local_ip" and content.get(output):
                        vm_local_ip = str(content.get(output))
                        ret_output['local_ip'] = vm_local_ip
                        #logger.debug("[HJC] VM Local IP = %s" %str(vm_local_ip))                        
                    
                    if output == "public_ip" and content.get(output):
                        vm_public_ip = str(content.get(output))
                        ret_output['public_ip'] = vm_public_ip
                        #logger.debug("[HJC] VM Public IP = %s" %str(vm_public_ip))
                    
                    if output == "SessionID" and content.get(output):
                        ret_output["SessionID"] = str(content.get(output))
            
            return 200, ret_output
        except Exception, e:
            err_msg = "Script Exception [%s] %s" % (str(e), sys.exc_info())
            logger.exception(err_msg)            
            return -500, err_msg
        
    def do_script(self, api_info, port_str=None, verbose=False):
        vm_conn = self.get_vnf_conn()
        if vm_conn is None:
            return -500, "Failed to get VNF VM Connection"
        
        try:
            url_info = api_info['requesturl'].split(";")
            protocol_name = url_info[0]  # http or https
            request_type = url_info[1]  # POST, PUT, GET, DELETE
            resource_name = url_info[2]  #/webapi/conf/proxy
            if port_str:
                url = "%s://%s:%s%s" % (protocol_name, self.get_mgmt_ip(), port_str, resource_name) # https://192.168.10.252:4433/webapi/conf/proxy
            else:
                url = "%s://%s%s" % (protocol_name, self.get_mgmt_ip(), resource_name) # https://192.168.10.252/webapi/conf/proxy
            logger.debug("[HJC] url = %s" %url)
            
            # build header
            headers = None
            if api_info.get('requestheaders') != None and len(api_info['requestheaders']) > 0:
                headers = api_info['requestheaders'] % tuple(api_info['requestheaders_args'])
            #logger.debug("[HJC] headers = %s" %str(headers))
            
            # build params
            params = None
            if api_info.get('paramformat') and len(api_info['paramformat']) > 0:
                params = api_info['paramformat'] % tuple(api_info['params'])
            #logger.debug("[HJC] params = %s" %str(params))
            
            # build cookie
            cookie = None
            if api_info.get('cookieformat') and len(api_info['cookieformat']) > 0:
                cookie = api_info['cookieformat'] % tuple(api_info['cookiedata'])
            
            body = None
            # build body
            if api_info.get('body') != None and len(api_info['body']) > 0:
                body = api_info['body'] % tuple(api_info['body_args'])
                result, body = self._replace_special_characters(body)
            #logger.debug("[HJC] body = %s" %str(body))
            
            if self.get_mgmt_ip().find("192.168.254") >= 0: #if self.action == "UPDATE":
                api = "curl -k "
            else:
                api = "curl -k "
            
            if cookie != None: api += "-b \"%s\" " %(cookie)
            
            if headers != None:
                header_list = headers.split("__")
                for h in header_list:
                    api += "-H \"%s\" " %(h)
            
            if params != None: api += "-d \'%s\' " %(params)
            
            if body != None: 
                body = body.replace('\\n', "%0A")
                api += "--data \"%s\" " %(body)
            
            if verbose:
                api += "-vX %s %s" %(request_type, url)
            else:
                api += "-X %s %s" %(request_type, url)
        
            logger.debug('rest api: %s' % api)
        except Exception, e:
            logger.exception(e)
            return -500, "Failed to compose api request (curl): %s" %str(e)
        
        try:
            result, content = vm_conn.exec_pexpect(api)
            if result < 0:
                logger.error("failed to call API of VNF VM %d %s" %(result, content))
                return result, content
                
            logger.debug("curl_result = %d" % (result))
            
            if verbose:
                result, content = self._parse_curl_result_verbose(content, api_info['output'])
            else:
                result, content = self._parse_curl_result(content)
            
            if result < 0:
                logger.error("failed to do script %s: %d %s" %(api_info['name'], result, content))
            return result, content
        except Exception, e:
            logger.exception(e)
            return -500, "Failed to perform api call: %s" %str(e)
        
    ################### Internal Methods ############################
    def _parse_curl_result(self, content):
        try:
            content_lines = content.strip().split('\n')
            result = -500
            line_no = 1
            content_output = {}
            content_output['content'] = ""
            ### TODO_START
            for line in content_lines:
                line = line.strip()
                line = line.rstrip('\x00')
                
                if line.find('HTTP/1.1') == 2:
                    logger.debug("curl result: found HTTP/1.1 at the line: %d, %s" %(line_no, line))
                    if line.find('200') >= 0:
                        result = 200
                    else:
                        line_list = line.split()
                        if len(line_list) > 2:
                            result = -int(line.split()[2])

                if line.startswith('1') and len(line) == 1:
                    content_output['success'] = True
                else:
                    content_output['content'] += line
                    
                line_no += 1
            result = 200
            logger.debug("content_output= %s" % content_output)
            ### TODO_END
        except Exception, e:
            logger.exception(e)
            error_msg = "failed to parse curl result %s" %content
            logger.error(error_msg)
            return -500, error_msg
        
        return result, content_output
    
    ################### Internal Methods ############################
    def _parse_curl_result_verbose(self, content, output_list=[]):
        try:
            content_lines = content.split('\n')
            result = -500
            line_no = 1
            content_output = {}
            ### TODO_START
            for line in content_lines:
                if line.find('HTTP/1.1') == 2:
                    logger.debug("curl result: found HTTP/1.1 at the line: %d, %s" %(line_no, line))
                    if line.find('200') >= 0:
                        result = 200
                    else:
                        line_list = line.split()
                        if len(line_list) > 2:
                            result = -int(line.split()[2])

                if line.find('1') >= 0 and len(line)==1:
                    logger.debug("curl result %d th line: %s" %(line_no, line))
                    content_output['success'] = True
                elif line.find('15  0') >= 0:
                    logger.debug("curl result %d th line: %s" %(line_no, line))
                    content_output['success'] = True
                else:
                    logger.debug("curl result %d th line: %s" %(line_no, line))
                    
                if output_list != None and len(output_list) > 0:
                    for output in output_list:
                        if line.find(output) >= 0:
                            try:
                                logger.debug("curl result %d th line: %s" %(line_no, line))
                                content_output[output] = line.split(output)[1].split('=')[1].strip()
                                logger.debug("The value of output %s: %s" %(output, content_output[output]))
                            except Exception, e:
                                logger.exception(e)        
                
                if len(output_list) == 0:
                    content_output["output"] = line
                    
                line_no += 1
            result = 200
            
            ### TODO_END
        except Exception, e:
            logger.exception(e)
            error_msg = "failed to parse curl result %s" %content
            logger.error(error_msg)
            return -500, error_msg
        
        return result, content_output
    
    def _replace_special_characters(self, original_str):
        SPC_PREFIX = "__SC__"
        SPC_POSTFIX = "__SC__"
        SPC_PERCENTAGE = SPC_PREFIX+"PERCENTAGE"+SPC_POSTFIX
        
        if original_str.find(SPC_PREFIX) < 0:
            logger.debug("No Special Characters found")
            return 200, original_str
        
        remaining_spc = True
        while remaining_spc is True:
            if original_str.find(SPC_PERCENTAGE) > 0:
                original_str = original_str.replace(SPC_PERCENTAGE, "%")
                logger.debug("Replaced Special Character: " + SPC_PERCENTAGE)
            else: 
                log.warning("Not supported Special Character")
                remaining_spc = False
            
            logger.debug("After Replacing Special Character: " + original_str)
            
            if original_str.find(SPC_PREFIX) < 0:
                remaining_spc = False
        
        return 200, original_str

    

class AXGATE_UTM(AXGATE_BASE):
    instances = {}
    
    ################### Essential Methods ############################
    def __init__(self, vnf_dict, local_mgmt_ip):        
        self.set_name(vnf_dict['name'])
        self.set_uuid(vnf_dict.get('uuid'))
        self.set_local_mgmt_ip(local_mgmt_ip)
        self.set_mgmt_ip(vnf_dict.get('mgmtip'))
        self.set_public_ip(None)
        self.set_user(vnf_dict.get('user', "axroot"))
        self.set_password(vnf_dict.get('password', "Admin12#$"))
        
        self.set_vnf_driver(None)
        self.set_vnf_conn(None)        
        
        # TODO: to be updated - should be stop at initial state, and there should be a method that update its status to running 
        self.set_status(VNFState.RUNNING)

    @staticmethod    
    def get_instance(vnf_dict):
        # singleton method that returns the DuruanUTM object for given local_mgmt_ip
        if vnf_dict.get('local_ip') is None:
            logger.error("Failed to create or find VNF Instance due to No Local IP Given: %s" %str(vnf_dict))
            return None

        try:
            logger.debug("AXGATE_UTM.instances for %s" % (str(vnf_dict)))
            local_mgmt_ip = vnf_dict['local_ip']
            
            instance = AXGATE_UTM.instances[local_mgmt_ip]
        except KeyError, e:
            instance = None
            logger.error(str(e))
        except Exception, e:
            logger.exception(e)
            
        if not instance:
            logger.debug("Create a new AXGATE_UTM.instances for %s" % (str(vnf_dict)))
            instance = AXGATE_UTM(vnf_dict, local_mgmt_ip)
            AXGATE_UTM.instances[local_mgmt_ip] = instance
        else:
            if vnf_dict.get('user'):
                instance.set_user(vnf_dict['user'])
            if vnf_dict.get('password'):
                instance.set_password(vnf_dict['password'])
            if vnf_dict.get('mgmtip'):
                instance.set_mgmt_ip(vnf_dict['mgmtip'])

        return instance
        
    def is_online(self):
        response = pyping.ping(self.get_local_mgmt_ip())    
        if response.ret_code == 0: # can connect                
            return True
        else: # cannot connect
            return False
    
    def run_script(self, script):
        try:
            result, content = self.do_script(script, "4433")
            
            if result < 0:    
                logger.error("Failed to do: %s" %(str(script)))
                raise Exception("Failed to do: %s" %(str(script)))
            
            return content
        except Exception, e:
            err_msg = "Script Exception [%s] %s" % (str(e), sys.exc_info())
            logger.exception(err_msg)            
            return err_msg
    
    def set_network_interface(self, sessionid, args):
        ret_output={}
        
        script = AXGATE_SCRIPT(sessionid).set_network_interface(args)
        content = self.run_script(script)
        
        return content
    
    def get_sw_version(self, sessionid):
        ret_output={}
        
        script = AXGATE_SCRIPT(sessionid).get_sw_version()
        content = self.run_script(script)
        
        return content
        
    ################### Necessary Methods for Interaction Other Scripts ############################
    def get_vnf_conn(self):
        if self.vnf_conn is None:
            try:
                if self.get_mgmt_ip() is None:
                    vm_access_ip = self.get_local_mgmt_ip()
                else:
                    vm_access_ip = self.get_mgmt_ip()
                logger.debug("VM Access IP: %s" %vm_access_ip)
                
                self.set_vnf_conn(self.get_vmconnector(vm_access_ip, self.get_user(), self.get_password(), 'rest_api', 'INIT'))
    
                logger.debug("Succeed to create a VNF Connection")           
            except Exception, e:
                logger.exception(e)
                self.vnf_conn = None

        return self.vnf_conn

    def check_connection(self, vm_conn=None, mgmt_ip=None, action_type='INIT'):
        if mgmt_ip is None:
            mgmt_ip = self.local_mgmt_ip
        
        if vm_conn is None:
            vm_conn = self.get_vmconnector(mgmt_ip, self.user, self.password, 'rest_api', action_type)
        
        result, content = vm_conn.check_connection(None, self.local_mgmt_ip, "4433")
        
        try:
            vnf_check_script = {
                'name': "get_session", 
                'requesturl': 'https;POST;/login.cgi', 
                'output':['SessionID'], 
                'requestheaders': "Content-type:application/x-www-form-urlencoded;charset=utf-8", 
                'requestheaders_args':[], 
                'paramformat': 'username=%s&password=%s', 
                "params": [self.user, self.password]
            }
        
            trial_no = 1
            while trial_no < 15:
                logger.debug("Trial %d to connect to the VNF VM" % (trial_no))
                
                if trial_no > 1:
                    time.sleep(20)
                
                result, content = self.do_script(vnf_check_script, "4433", verbose=True)
                logger.debug("Result: %s, %s" %(str(result), str(content)))
                if result >= 0:
                    break
                if result == -400 or result == -401:
                    break
                
                trial_no += 1
        except Exception, e:
            error_msg = "failed to check connection for the VM AXGATE-UTM %s" %(mgmt_ip)
            logger.exception(e)
            return -503, error_msg
        
        return result, content
    
    def setup_connection(self):
        try:
            if self.get_mgmt_ip() is None:
                vm_access_ip = self.get_local_mgmt_ip()
            else:
                vm_access_ip = self.get_mgmt_ip()
            logger.debug("VM Access IP: %s" %vm_access_ip)
            
            self.set_vnf_conn(self.get_vmconnector(vm_access_ip, self.get_user(), self.get_password(), 'rest_api', 'INIT'))

            logger.debug("Succeed to create a VNF Connection")           
 
            result, content = self.check_connection(self.get_vnf_conn())    
            if result < 0:
                logger.error("failed to make a connection to VM %d %s" % (result, content))
                raise Exception("failed to make a connection to VM %d %s" % (result, content))
            
            return 200, content            
        except Exception, e:
            logger.exception(e)
            return -500, "Failed to setup a connection to VNF VM"
    
    def get_interface_brief(self, script, action=None):
        ret_output={}
        try:
            result, content = self.do_script(script, "4433")
                
            if result > 0:
                pass
                
                if result < 0:    
                    logger.error("Failed to do: %s" %(str(script)))
                    raise Exception("Failed to do: %s" %(str(script)))
            
            return 200, content
        except Exception, e:
            err_msg = "Script Exception [%s] %s" % (str(e), sys.exc_info())
            logger.exception(err_msg)            
            return -500, err_msg