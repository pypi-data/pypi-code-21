from TTFramework.Core.InterfaceBase import *
from TTFramework.Core.FuncHelper import FuncHelper
from TTFramework.Core.Encryption import Encryption
from TTFramework.Core.Statistics import ConstStatistics
from TTFramework.Core.Permissions import check_permissions_is_login
from jinja2 import Template,Environment,FileSystemLoader



class TTAdmin(InterfaceBase):
    @check_permissions_is_login
    def Index(self, request):
        env = Environment(loader=FileSystemLoader(self.path + '/templete'))
        template = env.get_template('index.html')
        txt = template.render(locals())
        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})

    def login(self,request):
        _path = self.path + '/templete/login.html'
        if not FuncHelper.checkFileExists(_path):
            return request.Response(text='模版文件不存在！', mime_type='text/html')
        with open(_path,'r') as f:
            txt = f.read()
        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})

    def Logout(self,request):
        request.session.pop('is_login', None)
        return request.Response(code=302, text='Not Found', headers={"Location": 'login'})

    @check_permissions_is_login
    def ServiceModuleEdit(self,request):
        _module_name = request.query.get('module_name','')
        _module_option = None
        module_name = None
        if  _module_name != '':
            _module_option = self.Configer.send_pipe_command(('get_module_option_by_module_name', (True,_module_name)))
            module_name = _module_name

        env = Environment(loader=FileSystemLoader(self.path + '/templete'))
        template = env.get_template('service_module_edit.html')
        txt = template.render(locals())

        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})


    @check_permissions_is_login
    def ServiceModuleBrowse(self,request):
        _module_state_arr = self.ServiceManager.send_pipe_command(('get_module_state', None))

        env = Environment(loader=FileSystemLoader(self.path + '/templete'))
        template = env.get_template('service_module_browse.html')
        txt = template.render(locals())

        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})

    @check_permissions_is_login
    def InterfaceModuleEdit(self,request):
        _module_name = request.query.get('module_name','')
        _module_option = None
        module_name = None
        if  _module_name != '':
            _module_option = self.Configer.send_pipe_command(('get_module_option_by_module_name', (False,_module_name)))
            module_name = _module_name

        env = Environment(loader=FileSystemLoader(self.path + '/templete'))
        template = env.get_template('interface_module_edit.html')
        txt = template.render(locals())

        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})

    @check_permissions_is_login
    def InterfaceModuleBrowse(self,request):
        _module_state_arr = self.InterfaceManager.send_pipe_command(('get_module_state', None))

        env = Environment(loader=FileSystemLoader(self.path + '/templete'))
        template = env.get_template('interface_module_browse.html')
        txt = template.render(locals())

        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})

    @check_permissions_is_login
    def System(self,request):
        _module_option = None
        _module_option = self.Configer.send_pipe_command(('get_system_option',None))
        env = Environment(loader=FileSystemLoader(self.path + '/templete'))
        template = env.get_template('system.html')
        txt = template.render(locals())
        return request.Response(text=txt, mime_type='text/html',
                                headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})

    def test(self,request):
        _v = self._create_response(APIResponse.SUCCESS)
        return _v
        random_str = "woshi我是一个粉刷匠1231繁體testひらがな"+FuncHelper.get_random_str(20)
        result = 'source:' + random_str

        md5_str = Encryption.encrypt_md5_by_str(random_str)
        result = result + '\n' + 'md5str:' + md5_str

        key = 'wansanmaomaowan0'
        value = Encryption.encrypt_aes(random_str, key)
        result = result + '\n' + 'encrypt_aes:' + value

        value = Encryption.decrypt_aes(value, key)
        result = result  + '\n' + 'decrypt_aes:' + value
        return request.Response(text=result)

    def rest_login(self,request):
        result = {}
        result['state'] = 'success'
        try:
            _dict = request.form
            if (_dict['user_name'] == self.Configer.send_pipe_command(('supper_user_name', None))) and (_dict['password'] == self.Configer.send_pipe_command(('supper_user_password', None))):
                result['data'] = '登陆成功'
                request.session['is_login'] = True
            else:
                result['state'] = 'failed'
                result['info'] = '用户名或密码错误'
        except Exception as e:
            result['state'] = 'failed'
            result['info'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')


    def rest_cpu_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            values = self.Statistics.computer_state_list
            _time = []
            _used = []
            for _data in values:
                _time.append(_data[ConstStatistics.TIME])
                _used.append(_data[ConstStatistics.CPU])
            data = {}
            data[ConstStatistics.TIME] = _time
            data[ConstStatistics.CPU] = _used
            result['data'] = data
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')


    def rest_mem_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            _times = []
            _used = []
            _total = []
            _percent = []
            for _data in self.Statistics.computer_state_list:
                _times.append(_data[ConstStatistics.TIME])
                _used.append(_data[ConstStatistics.MEM][ConstStatistics.MEM_USED])
                _total.append(_data[ConstStatistics.MEM][ConstStatistics.MEM_TOTAL])
                _percent.append(_data[ConstStatistics.MEM][ConstStatistics.MEM_PERCENT])
            data = {}
            data[ConstStatistics.TIME] = _times
            data[ConstStatistics.MEM_USED] = _used
            data[ConstStatistics.MEM_TOTAL] = _total
            data[ConstStatistics.MEM_PERCENT] = _percent
            result['data'] = data
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')

    def rest_io_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            _times = []
            _read = []
            _write = []
            for _data in self.Statistics.computer_state_list:
                _times.append(_data[ConstStatistics.TIME])
                _read.append(_data[ConstStatistics.IO][ConstStatistics.IO_READ])
                _write.append(_data[ConstStatistics.IO][ConstStatistics.IO_WRITE])

            data = {}
            data[ConstStatistics.TIME] = _times
            data[ConstStatistics.IO_READ] = _read
            data[ConstStatistics.IO_WRITE] = _write
            result['data'] = data
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')

    def rest_net_io_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            _times = []
            _send = []
            _recv = []
            for _data in self.Statistics.computer_state_list:
                _times.append(_data[ConstStatistics.TIME])
                _send.append(_data[ConstStatistics.NET_IO][ConstStatistics.NET_IO_SEND])
                _recv.append(_data[ConstStatistics.NET_IO][ConstStatistics.NET_IO_RECV])

            data = {}
            data[ConstStatistics.TIME] = _times
            data[ConstStatistics.NET_IO_SEND] = _send
            data[ConstStatistics.NET_IO_RECV] = _recv
            result['data'] = data
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')

    def rest_module_statics_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            module_all_visitor_count = self.Statistics.module_all_visitor_count
            send_bytes_count = self.Statistics.bytes2human(self.Statistics.send_bytes_count)
            module_interface_count, module_service_count = self.Configer.send_pipe_command(('module_count', None))
            data = {}
            data['module_all_visitor_count'] = module_all_visitor_count
            data['send_bytes_count'] = send_bytes_count
            data['module_interface_count'] = module_interface_count
            data['module_service_count'] = module_service_count
            result['data'] = data
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')

    @check_permissions_is_login
    def rest_save_service_set_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            if request.form:
                service_name = request.form.get('service_name','')
                service_file_path = request.form.get('service_file_path','')
                git_url = request.form.get('git_url', '')
                git_username = request.form.get('git_username', '')
                git_passwd = request.form.get('git_passwd', '')
                database_ip = request.form.get('database_ip', '')
                databse_port = int(request.form.get('databse_port', 0))
                database_db_name = request.form.get('database_db_name', '')
                database_user_name = request.form.get('database_user_name', '')
                database_passwd = request.form.get('database_passwd', '')
                database_pool_size = int(request.form.get('database_pool_size', 20))
                loop_time = request.form.get('loop_time', 5)
                _o_params = request.form.get('other_params', '{}')
                if _o_params != '':
                    other_params = FuncHelper.json_to_dict(_o_params)
                else:
                    other_params = {}
                service_enable = (request.form.get('service_enable', 'True')).lower()=='true'
                is_register_zookeeper = (request.form.get('is_register_zookeeper', 'False')).lower() == 'true'
                message = ''
                if service_name == '':
                    message = '服务模块名不能为空！'
                if service_file_path == '':
                    message = '服务模块路径不能为空！'

                if message != '':
                    result['state'] = 'failed'
                    result['message'] = message
                    return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')
                self.Configer.send_pipe_command(('create_new_service_node', (service_name,service_enable,service_file_path,is_register_zookeeper,
                                                      git_url,git_username,git_passwd,loop_time,
                                                      database_ip,databse_port,database_db_name,database_user_name,database_passwd,database_pool_size,
                                                      other_params)))
                self.Configer.send_pipe_command(('write_config_file', None))
            else:
                result['state'] = 'failed'
                result['message'] = '参数不存在!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')

    @check_permissions_is_login
    def rest_stop_service(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            service_name = request.form.get('module_name', '')
            if service_name == '':
                result['state'] = 'failed'
                result['message'] = '模块名不允许为空!'
            else:
                _value = self.ServiceManager.send_pipe_command(('stop_module_by_module_name', service_name))
                if not _value:
                    result['state'] = 'failed'
                    result['message'] = '执行失败：模块可能是未运行状态!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')

    @check_permissions_is_login
    def rest_restart_service(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            service_name = request.form.get('module_name', '')
            if service_name == '':
                result['state'] = 'failed'
                result['message'] = '模块名不允许为空!'
            else:
                _value = self.ServiceManager.send_pipe_command(('start_module_by_module_name', service_name))
                if not _value:
                    result['state'] = 'failed'
                    result['message'] = '执行失败：模块可能是未运行状态,请刷新查看状态是否正常!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')

    @check_permissions_is_login
    def rest_delete_service(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            service_name = request.form.get('module_name', '')
            if service_name == '':
                result['state'] = 'failed'
                result['message'] = '模块名不允许为空!'
            else:
                self.ServiceManager.send_pipe_command(('stop_module_by_module_name', service_name))
                self.Configer.send_pipe_command(('delete_module_by_module_name', (True, service_name)))
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')

    @check_permissions_is_login
    def rest_save_interface_set_data(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            if request.form:
                interface_name = request.form.get('interface_name','')
                interface_file_path = request.form.get('interface_file_path','')
                swagger_url = request.form.get('swagger_url', '')
                git_url = request.form.get('git_url', '')
                git_username = request.form.get('git_username', '')
                git_passwd = request.form.get('git_passwd', '')
                database_ip = request.form.get('database_ip', '')
                databse_port = int(request.form.get('databse_port', 0))
                database_db_name = request.form.get('database_db_name', '')
                database_user_name = request.form.get('database_user_name', '')
                database_passwd = request.form.get('database_passwd', '')
                database_pool_size = int(request.form.get('database_pool_size', 20))
                _o_params = request.form.get('other_params', '{}')
                if _o_params != '':
                    other_params = FuncHelper.json_to_dict(_o_params)
                else:
                    other_params = {}
                interface_enable = (request.form.get('interface_enable', 'True')).lower()=='true'
                is_register_zookeeper = (request.form.get('is_register_zookeeper', 'False')).lower() == 'true'
                message = ''
                if interface_name == '':
                    message = '接口模块名不能为空！'
                if interface_file_path == '':
                    message = '接口模块路径不能为空！'

                if message != '':
                    result['state'] = 'failed'
                    result['message'] = message
                    return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')
                self.Configer.send_pipe_command(('create_new_interface_node', (swagger_url,interface_name,interface_enable,interface_file_path,is_register_zookeeper,git_url,git_username,git_passwd,
                                  database_ip, databse_port, database_db_name, database_user_name, database_passwd,
                                  database_pool_size, other_params)))
                self.Configer.send_pipe_command(('write_config_file', None))
            else:
                result['state'] = 'failed'
                result['message'] = '参数不存在!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')

    @check_permissions_is_login
    def rest_stop_interface(self,request):
        try:
            result = {}
            result['state'] = 'failed'
            result['message'] = '接口停止,请修改参数为不启用,然后重启整个服务!'
            return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')
            service_name = request.form.get('module_name', '')
            if service_name == '':
                result['state'] = 'failed'
                result['message'] = '模块名不允许为空!'
            else:
                _value = self.InterfaceManager.send_pipe_command(('unbinding_module_by_module_name', service_name))
                if not _value:
                    result['state'] = 'failed'
                    result['message'] = '执行失败：模块可能是加载状态!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')

    @check_permissions_is_login
    def rest_restart_interface(self,request):
        try:
            result = {}
            result['state'] = 'failed'
            result['message'] = '接口重启只能重启整个服务!'
            return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')
            service_name = request.form.get('module_name', '')
            if service_name == '':
                result['state'] = 'failed'
                result['message'] = '模块名不允许为空!'
            else:
                _value = self.InterfaceManager.send_pipe_command(('binding_module_by_module_name', service_name))
                if not _value:
                    result['state'] = 'failed'
                    result['message'] = '执行失败：模块可能是已经绑定,请刷新查看状态是否正常!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')

    @check_permissions_is_login
    def rest_delete_interface(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            service_name = request.form.get('module_name', '')
            if service_name == '':
                result['state'] = 'failed'
                result['message'] = '模块名不允许为空!'
            else:
                self.InterfaceManager.send_pipe_command(('unbinding_module_by_module_name', service_name))
                self.Configer.send_pipe_command(('delete_module_by_module_name', (False, service_name)))
                result['state'] = 'failed'
                result['message'] = '接口已经删除,重启服务后生效!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result), mime_type='application/json')

    @check_permissions_is_login
    def rest_save_system_option(self,request):
        try:
            result = {}
            result['state'] = 'success'
            result['message'] = ''
            if request.form:
                data_path = request.form.get('data_path','')
                host = request.form.get('host','0.0.0.0')
                port = int(request.form.get('port', 80))
                thread_count = int(request.form.get('thread_count', 1))
                fastdfs_config_file_path = request.form.get('fastdfs_config_file_path', '')
                module_prefix = request.form.get('module_prefix', '')
                file_size = int(request.form.get('file_size', 2048))
                white_list_ip = request.form.get('white_list_ip', ['*'])

                supper_user_name = request.form.get('supper_user_name', 'admin')
                supper_passwd = request.form.get('supper_passwd', '123456')

                ldap_base_dn = request.form.get('ldap_base_dn', '')
                ldap_prefix = request.form.get('ldap_prefix', '')
                ldap_url = request.form.get('ldap_url', '')
                check_service_alive_time = int(request.form.get('check_service_alive_time', 60))
                encryptor_key = request.form.get('encryptor_key', '')
                home_page_module_name = request.form.get('home_page_module_name', '')

                database_ip = request.form.get('database_ip', '127.0.0.1')
                databse_port = int(request.form.get('databse_port', 5432))
                database_user_name = request.form.get('database_user_name', '')
                database_passwd = request.form.get('database_passwd', '')
                database_db_name = request.form.get('database_db_name', '')
                database_pool_size = int(request.form.get('database_pool_size', 20))

                logger_level = int(request.form.get('logger_level', 0))

                debug = (request.form.get('debug', 'True')).lower()=='true'

                self.Configer.send_pipe_command(('create_new_options_node', (debug,data_path,file_size,host,port,thread_count,white_list_ip,supper_user_name,supper_passwd,
                                ldap_base_dn,ldap_prefix,ldap_url,fastdfs_config_file_path,module_prefix,check_service_alive_time,
                                encryptor_key,home_page_module_name,logger_level,
                                database_ip, databse_port, database_db_name, database_user_name, database_passwd,database_pool_size)))
                self.Configer.send_pipe_command(('write_config_file', None))
            else:
                result['state'] = 'failed'
                result['message'] = '参数不存在!'
        except Exception as e:
            result['state'] = 'failed'
            result['message'] = str(e)
        return request.Response(text=FuncHelper.dict_to_json(result),mime_type='application/json')