'''
vnfm_core implements all the methods of VNFM.
'''
__author__="Namgon Kim"
__date__ ="$16-oct-2017 16:54:29$"

import requests
import sys
import json
from kt_vnfm.utils import auxiliary_functions as af

from httplib import HTTPException
import time

import commands
import pexpect

from types import *

import kt_vnfm.utils.log_manager as log_manager
logger = log_manager.LogManager.get_instance()

class vmconnector_restapi():
    def __init__(self, name, host, uuid=None, user=None, passwd=None, url=None, debug=True, config={}, action='INIT'):
        '''using common constructor parameters. In this case 
        'url' is the ip address or ip address:port,
        ''' 
        logger.debug("[HJC] IN")
        self.id        = uuid
        self.name      = name
        self.host = host
        if not host:
            raise TypeError, 'host param can not be NoneType'
        self.url       = url
        self.user      = user
        self.passwd    = passwd
        self.config              = config
        self.debug               = debug
        self.action    = action
        self.reload_client       = True   
    
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
        else:
            raise KeyError("Invalid key '%s'" %str(index))

    def exec_pexpect(self, cmd, timeout_=60, expect_dict={}):
        result = 200
        content = "None"
        
        try:
            #logger.debug("do command %s" %cmd)
            child = pexpect.spawn(cmd, timeout=timeout_)
            #child.logfile = sys.stdout
            
            resp = child.expect(['password: ', pexpect.EOF, 'No route to host'])
            
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
                logger.debug("Success to do the command")
                content = child.before
            elif resp == 2:
                result = -503
                content = "Wati for completion of VM booting"
                logger.error(content)                
           
            logger.debug('result: %s' %content)
        except pexpect.TIMEOUT:
            result = -500
            content = 'failed to pexpect to %s. Timeout occurred' %self.host
            logger.error(content)
        finally:
            child.close()
        
        return result, content
    
    def check_connection(self, script={}, vnf_local_ip=None, port_str=None):
        if self.host == None:
            return -400, "No Host Info"
        
        logger.debug("check_connection using the script: %s" % str(script))
        
        try:
            ssh_cmd = 'ssh-keygen -f \"/root/.ssh/known_hosts\" -R %s' %(self.host)
            logger.debug('command: %s' %ssh_cmd)
            
            r, c = self.exec_pexpect(ssh_cmd)
        except:
            error_msg = "failed to ssh-keygen -f for %s" %(self.host)
            logger.exception(error_msg)
            
        try:
            if vnf_local_ip:
                ssh_cmd = 'ssh-keygen -f \"/root/.ssh/known_hosts\" -R %s' %(vnf_local_ip)
                logger.debug('command: %s' %ssh_cmd)
                
                r, c = self.exec_pexpect(ssh_cmd)
        except:
            error_msg = "failed to ssh-keygen -f for %s" %(self.host)
            logger.exception(error_msg)
        
        if script == None or len(script) < 1:
            logger.debug("No checking script")
            return 200, "No Test"
        
        try:
            trial_no = 1
            while trial_no < 15:
                logger.debug("Trial %d to connect to the VNF VM" % (trial_no))
                
                if trial_no > 1:
                    time.sleep(20)
                
                result, content = self.do_script(script, port_str)
                logger.debug("Result: %s, %s" %(str(result), str(content)))
                if result >= 0:
                    break
                if result == -400 or result == -401:
                    break
                
                trial_no += 1
        except Exception, e:
            error_msg = "failed to check connection for the VM %s %s" %(self.name, self.host) 
            logger.exception(e)
            return -503, error_msg        
        
        return result, content
    
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
    
    def do_script(self, api_info, port_str=None):
        # build url
        try:
            url_info = api_info['requesturl'].split(";")
            protocol_name = url_info[0]  # http or https
            request_type = url_info[1]  # POST, PUT, GET, DELETE
            resource_name = url_info[2]  #/webapi/conf/proxy
            if port_str:
                url = "%s://%s:%s%s" % (protocol_name, self.host, port_str, resource_name) # https://192.168.10.252:4433/webapi/conf/proxy
            else:
                url = "%s://%s%s" % (protocol_name, self.host, resource_name) # https://192.168.10.252/webapi/conf/proxy
            #logger.debug("[HJC] url = %s" %url)
            
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
            
            # build api
            #api = "curl --insecure -b %s -H \"%s\" -vX %s %s -d \'%s\'" % (self.net_ns, cookie, header, request_type, url, params)
            
            if self.host.find("192.168.254") >= 0: #if self.action == "UPDATE":
                api = "curl --insecure -k "
            else:
                api = "curl --insecure -k " %(self.net_ns)
            
            if cookie != None: api += "-b %s " %(cookie)
            
            if headers != None:
                header_list = headers.split("__")
                for h in header_list:
                    api += "-H \"%s\" " %(h)
            
            if params != None: api += "-d \'%s\' " %(params)
            
            if body != None: api += "-d \'%s\' " %(body)
            
            api += "-vX %s %s" %(request_type, url)
        
            logger.debug('rest api: %s' % api)
        except  Exception, e:
            error_msg = "failed to compose a curl command (rest api type) due to Exception: %s" %str(e) 
            logger.exception(error_msg)
            return -500, error_msg
        
        result, content = self.exec_pexpect(api)
        if result < 0:
            logger.error("failed to call API of VNF VM %d %s" %(result, content))
            return result, content
            
        logger.debug("curl_result = %d" % (result))
        
        result, content = self.parse_curl_result(content, api_info['output'])
        if result < 0:
            logger.error("failed to do script %s: %d %s" %(api_info['name'], result, content))
        
        #logger.debug("%s end" %api_info['name'])
        
        return result, content
    
    def copy_ssh_key(self, path='/root/.ssh/id_rsa.pub'):
        options = '-oStrictHostKeyChecking=no'
        
        if self.host.find("192.168.254") >= 0: #if self.action == "UPDATE":
            mkdir_cmd = "ssh %s %s@%s mkdir .ssh" % (options, self.user, self.host)
            result1, content1 = self.exec_pexpect(mkdir_cmd)
            
            scp_cmd = "scp %s %s %s@%s:.ssh/authorized_keys" % (options, path, self.user, self.host)
            logger.debug('command: %s' % scp_cmd)
            
            result, content = self.exec_pexpect(scp_cmd)
        else:
            mkdir_cmd = "ssh %s %s@%s mkdir .ssh" % (self.net_ns, options, self.user, self.host)
            result1, content1 = self.exec_pexpect(mkdir_cmd)
            
            scp_cmd = "scp %s %s %s@%s:.ssh/authorized_keys" % (self.net_ns, options, path, self.user, self.host)
            logger.debug('command: %s' % scp_cmd)
            
            result, content = self.exec_pexpect(scp_cmd)
        
        return result, content
    
    def do_command(self, command, timeout=20):
        logger.debug("[HJC] IN")
        
        try:
            logger.debug("curl_cmd = %s" % (command))
            result, content = self.exec_pexpect(command, timeout)
            if result < 0:
                logger.error("failed due to vm access failure %d %s" %(result, content))
                return result, content
                
            logger.debug("curl_result = %d" % (result))
            
        except  Exception, e:
            error_msg = "failed to do command (rest api type) due to Exception: %s" %str(e) 
            logger.exception(error_msg)
            return -500, error_msg
        
        return result, content
        
    def parse_curl_result(self, content, output_list=[]):
        try:
            content_lines = content.split('\n')
            result = -500
            line_no = 1
            content_output = {}
            for line in content_lines:
                if line.find('HTTP/1.1') == 2:
                    if line.find('200') >= 0:
                        result = 200
                    else:
                        line_list = line.split()
                        if len(line_list) > 2:
                            result = -int(line.split()[2])

                if line.find('success') >= 0:
                    logger.debug("curl result %d th line: %s" %(line_no, line))
                    try:
                        json_str_line = line.replace("'","\"")
                        json_line = json.loads(json_str_line)
                        content_output['success']=json_line['success']
                        if content_output['success'] == "true":
                            logger.debug("[****HJC****] the value of success field is string or unicode" )
                            content_output['success'] = True
                    except Exception, e:
                        #logger.exception("Exception: %s" %str(e))
                        pass

                if output_list != None and len(output_list) > 0:
                    for output in output_list:
                        if line.find(output) >= 0:
                            if output == 'WP_SESSID':
                                if line.find('Set-Cookie') >= 0:
                                    logger.debug("curl result %d th line: %s" %(line_no, line))
                                    content_output[output] = line.split(':')[1].split(';')[0].split('=')[1]
                                    logger.debug("WP_SESSID: %s" %content_output[output])
                            elif output == 'token':
                                #TODO
                                logger.debug("curl result %d th line: %s" %(line_no, line))
                                try:
                                    line_list = line.split(output+"\":\"")
                                    logger.debug("target line list: %s" %str(line_list))
                                    content_output[output] = line_list[1].split("\"")[0]
                                    logger.debug("output key: %s, value: %s" %(output, content_output[output]))
                                except Exception, e:
                                    logger.exception(str(e))
                                    continue
                            else:
                                logger.debug("curl result %d th line: %s" %(line_no, line))
                                content_output[output] = line.split(output+":")[1]
                                logger.debug("output key: %s, value: %s" %(output, content_output[output]))        
                line_no += 1
        except Exception, e:
            logger.exception("Exception: %s" %str(e))
            error_msg = "failed to parse curl result %s" %content
            logger.error(error_msg)
            return -500, error_msg
        
        return result, content_output
