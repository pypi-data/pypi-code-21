"""This client lib provides API to access an IoT server instance,
which in turn, provides information to sensor devices monitored by server.
"""

from __future__ import absolute_import
import json

try:
    from . import IoTurllib3 as IoTurllib
except ImportError:
    from . import IoTurllib2 as IoTurllib


# import IoTurllib3 as IoTurllib




def get_compatible_revision():
    return 844


def is_compatible_version(sver, lver):
    """
    Check version compatibility
    
    :param sver: 
    :param lver: 
    :return: 
    """
    # smajor, sminor = str(sver).split('.')[:2]
    # lver = lver[1:]
    # return lver[0] == smajor[0]

    sminor, rev = str(sver).split('.')[-2:]
    # print(str(sminor) + " "+ str(rev))
    return int(rev) <= int(lver)


def is_compatible_legacy_version(sver):
    return int(sver) <= 844
    # smajor, sminor = str(sver).split('.')[:2]

    # return smajor == '1' and 0 <= int(sminor) <= 10


class Group:
    """Creates an IoT Group instance connected to one server,
    which can form a cluster of several servers, as configured by the IoT application.

    :param str server: server url, such as 'http://localhost:9001'
    :param str group: a group of devices that belong to one entity,
                      as 'me' to access local devices or 'friend1'
    :param int timeout: request timeout in seconds
    :param bool ssl_untrusted: request lets true untrusted ssl certificate
    :param str ssl_cert_file: client ssl certificate file
    :param str ssl_cert_pass: client ssl certificate password
    """

    def __init__(self, server, group, timeout=10, version='v1', ssl_untrusted=True, ssl_cert_file=None,
                 ssl_cert_pass=None, username=None, password=None, keep_alive=True, keep_alive_timeout=10):

        self.params = {
            "server": server,
            "group": group,
            "timeout": timeout,
            "version": version,
            "ssl_untrusted": ssl_untrusted,
            "ssl_cert_file": ssl_cert_file,
            "ssl_cert_pass": ssl_cert_pass,
            "username": username,
            "password": password,
            "keep_alive": keep_alive,
            "keep_alive_timeout": keep_alive_timeout

        }

        self.server = server + '/api/' + version
        self.group = group
        self.server_url = self.server + '/' + group
        self.timeout = timeout
        self.context = None
        self.auth_header = None

        if username and password:
            self.auth_header = IoTurllib.encode_auth_header(username, password)

        if (self.server_url.startswith('https://')):
            self.context = IoTurllib.get_context(untrusted=ssl_untrusted, cert_file=ssl_cert_file,
                                                 cert_pass=ssl_cert_pass)

        self.request = IoTurllib.RequestHandler(self.context, self.auth_header,
                                                keep_alive=keep_alive, keep_alive_timeout=keep_alive_timeout)

        # Check version
        """
        try:
            sver = self.request.get(self.server_url + '/version.json', self.timeout)
        except Exception as e:
            
            if str( e).find("400") != -1:                
                sver = self.request.get(server + '/me/version.json', self.timeout)
                if not is_compatible_legacy_version(sver['build']):
                    raise RuntimeError('Version of the IoT lib does not match with the legacy server.')
                self.server = server
                self.server_url = self.server + '/' + group
                return
            else:
                raise RuntimeError('Unable to verify server version')
        
        #print(str(sver))    
        """
        sver = self.request.get(self.server_url + '/version.json', self.timeout)

        if not is_compatible_version(sver['api'], get_compatible_revision()):
            raise RuntimeError('Version of the IoT lib does not match with the server. Please update to newer version.')


            # if not is_compatible_version(sver['major'] + '.' + sver['minor'], __version__):
            #    raise RuntimeError('Version of the IoT lib does not match with the server.')

    def clone(self):
        """
        Clone this Group
        :return: 
        """
        me = Group(self.params['server'],
                   self.params['group'],
                   timeout=self.params['timeout'],
                   version=self.params['version'],
                   ssl_untrusted=self.params['ssl_untrusted'],
                   ssl_cert_file=self.params['ssl_cert_file'],
                   ssl_cert_pass=self.params['ssl_cert_pass'],
                   username=self.params['username'],
                   password=self.params['password'],
                   keep_alive=self.params['keep_alive'],
                   keep_alive_timeout=self.params['keep_alive_timeout'])
        return me

    def get(self, uri, params=None):
        """
        Sends generic GET request
        
        :param str uri: resource uri
        :param dict params: HTTP request parameters
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        if not uri.startswith("/"):
            uri = "/" + uri
        uri = self.server + uri
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def post(self, uri, data, dump_json=True):
        """
        Sends generic POST request
        
        :param str uri: resource uri
        :param dict data: Request body
        :param dump_json: convert json data to string if True
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        if not uri.startswith("/"):
            uri = "/" + uri
        uri = self.server + uri
        if dump_json:
            data = json.dumps(data)
        return self.request.post(uri, data, self.timeout)

    def delete(self, uri, params=None):
        """
        Sends generic DELETE request
        
        :param str uri: resource uri
        :param dict params: HTTP request parameters
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        if not uri.startswith("/"):
            uri = "/" + uri
        uri = self.server + uri
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.delete(uri, self.timeout)

    def get_device_list(self, inactive=False):
        """Gets list of devices from server.

        :returns: list of devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        uri = self.server_url + ".json"
        if not inactive:
            uri += "?active=true"
        return self.request.get(uri, self.timeout)

    def get_service_list(self):
        """Gets list of running services from server.

        :returns: list of devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        uri = self.server_url + "/services.json"

        return self.request.get(uri, self.timeout)

    def get_service_pin(self, name):
        """Request service PIN number required for connection
        :returns: pin number
        """
        uri = self.server_url + "/services/pin/" + str(name)

        return self.request.get(uri, self.timeout)

    def get_bluetooth_list(self, after=None):
        """Fetches list of devices connected through bluetooth.

        :returns: list of bluetooth devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        return self._get_list(self.server_url + "/bluetooth.json", after=after, timeout=90)

    def get_serial_list(self, after=None):
        """Fetches list of devices connected through serial ports.

        :returns: list of serial devices
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        return self._get_list(self.server_url + "/serial.json", after=after, timeout=30)

    def _get_list(self, uri, after=None, timeout=None):
        if after:
            uri += '?after=' + str(after)
        return self.request.get(uri, timeout if timeout else self.timeout)

    def get_adapter_status(self, adapter, level=None):
        """
        Get connected adapter status
        
        :param str adapter: adapter preset or communication port
        :param str level: limit status results by protocol level (phy, frame, ec, trans, msg)
        :returns: adapter status in json form
        """
        uri = self.server_url + "/serial/" + adapter
        if level:
            uri += "/" + level
        return self.request.get(uri, self.timeout)

    def set_adapter_setting(self, adapter, level, data):
        """
        Set protocol parameter
        
        :param str adapter: adapter preset or communication port
        :param str level: limit status results by protocol level (phy, frame, ec, trans, msg)
        :param data: data format {"setting_name":"value"}
        :returns: operation result
        """
        uri = self.server_url + "/serial/" + adapter + "/" + level
        return self.request.post(uri, json.dumps(data), self.timeout)

    def get_activity(self, params=None):
        """
        Get latest server activity logs
        
        :param int limit: max number of returned logs
        :returns: activity logs
        :rtype: list of dicts
        :raises: HTTPError, socket.timeout
        """
        uri = self.server_url + '/activity.json'
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def push_notification(self, data):
        """
        Sends generic POST request
        
        :param str uri: resource uri
        :param dict data: Request body
        :param dump_json: convert json data to string if True
        :returns: Resource response
        :rtype: depending on resource
        :raises: HTTPError, socket.timeout
        """
        uri = self.server_url + '/activity.json'
        return self.request.post(uri, json.dumps(data), self.timeout)

    def time(self):
        """Returns current server time.

        :returns: current server time
        :rtype: float
        """
        ts = self.request.get(self.server_url + '/servertime.json', self.timeout)
        try:
            return float(ts['time'])
        except:
            return None

    def version(self):
        """Returns current server time.

        :returns: current server time
        :rtype: float
        """
        return self.request.get(self.server_url + '/version.json', self.timeout)

    def run_script(self, script_name, phy_name):
        """Runs a script on a server.

        :returns: state of the script.
        """
        data = {'alias': script_name, 'phy': phy_name}
        return self.request.post(self.server + "/terminal/aliases",
                                 json.dumps(data), self.timeout)

    def kill_script(self):
        """Kills currently running script on a server.

        :returns: state of the last script
        """
        self.do('$kill')

    def do(self, command, params=''):
        """Sends a command to a server.
        Refer to server help for a list of available commands, obtainable with the $help command.

        :param str command: name of the command to be executed
        :param str params: optional parameters for the command
        """
        data = {
            'command': command,
            'parameters': params
        }
        return self.request.post(self.server + "/terminal/commands",
                                 json.dumps(data), self.timeout)

    def load_virtual_device(self, data, owner=None):
        """
        Create virtual device
        """
        uri = self.server_url + "/virtual"
        return self.request.post(uri, json.dumps(data), self.timeout)

    def remove_device(self, device):
        """
        Remove given active device from protocol stack
        """
        uri = self.server_url + "/" + str(device)
        return self.request.delete(uri, self.timeout)

    def get_property_list(self, identifier):
        """Retrieves a list of properties related to the device.
        :returns: list of property names
        :rtype: list
        """
        uri = self.server_url + "/"
        uri += identifier + "/properties" + '.json'
        return self.request.get(uri, self.timeout)

    def add_params_to_uri(self, uri, params=None):
        if params:
            qp = []
            for k, v in params.items():
                qp.append(k + '=' + str(v))

            qs = '?' + '&'.join(qp) or ''
            uri += qs

        return uri

    def get_property(self, identifier, prop, params=None):
        """Fetches value of *prop* property.
        The object returned has a definite structure:
        ``{ prop: {data: <value>}, time: <tstmp> }``

        :param str identifier: property group identifier
        :param str prop: name of the property
        :returns: value of the property
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.server_url + "/"
        uri += identifier + "/properties/" + prop + '.json'

        # if params :
        #    qp = []
        #    for k,v in params.items():
        #        qp.append(k + '=' + str(v))
        #   
        #    qs = '?' + '&'.join(qp) or ''
        #    uri += qs
        # print(uri)
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def set_property(self, identifier, prop, value, append=False):
        """Sets or overwrites the value of the *prop* property with *val* value.
        The *val* passed is stored and enclosed in:
        ``{prop: {data: <val>}}``

        :param str identifier: property group identifier
        :param str prop: name
        :param str|dict|number value: value
        :returns: result with structure ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.server_url + "/"
        uri += identifier + "/properties/" + prop + '.json'

        if append:
            uri += '?append=true'

        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_property(self, identifier, prop, params=None):
        """Deletes the `prop` property.
        The entire property, not only its value, is removed.
        
        :param str identifier: property group identifier
        :param str prop: name
        :return: response with structure: ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.server_url + "/"
        uri += identifier + "/properties/" + prop + '.json'

        uri = self.add_params_to_uri(uri, params=params)

        return self.request.delete(uri, self.timeout)

    def get_arptable(self, params=None):
        """
        Get arptable
        :param params: 
        :return: 
        """

        uri = self.server + "/arptable"
        uri = self.add_params_to_uri(uri, params=params)

        return self.request.get(uri, self.timeout)

    def credentials(self):
        """
        Get current user credentials
        """
        uri = self.server + "/credentials"

        return self.request.get(uri, self.timeout)

    def get_users(self, principal_filter=None, username=None, key=None, pending=False, user_type=None):
        """
        Get user credentials according to given filters
        
        :param str filter: user principal info filter
        :param str key: user public key
        :param bool pending: pending users
        :param cred_type: credentials type, either password or certificate
        """
        uri = self.server + "/credentials/users"
        if pending:
            uri = uri + "/pin"
        if key:
            uri += "?key=" + str(key)
        elif principal_filter:
            uri += "?filter=" + str(principal_filter)
        elif username:
            uri += "?username=" + str(username)

        if user_type:
            uri = uri + ("&" if (key or principal_filter or username) else "?") + "type=" + str(user_type)

        return self.request.get(uri, self.timeout)

    def set_user(self, value, pending=False):
        """
        Set user credentials 
        
        :param str value: credentials json data
        
        """
        uri = self.server + "/credentials/users"
        if pending:
            uri = uri + "/pin"
        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_user(self, principal_filter=None, username=None, key=None, pending=False, user_type=None):
        """
        Delete user credentials
        
        :param str filter: user principal info filter
        :param str key: user public key     
        :param bool pending: pending pin users         
        :param cred_type: credentials type, either password or certificate
        """
        uri = self.server + "/credentials/users"
        if pending:
            uri = uri + "/pin"

        if key:
            uri += "?key=" + str(key)
        elif principal_filter:
            uri += "?filter=" + str(principal_filter)
        elif username:
            uri += "?username=" + str(username)

        if user_type:
            uri = uri + ("&" if (key or principal_filter or username) else "?") + "type=" + str(user_type)

        return self.request.delete(uri, self.timeout)

    def register_user(self, pin, name=None):
        """
        Register user credentials with PIN number 
        
        :param int pin: PIN number
        
        """
        uri = self.server + "/credentials/users/register"
        uri += "?pin=" + str(pin)
        if name:
            uri += "&name=" + str(name)
        return self.request.get(uri, self.timeout)

    def reset_user(self, pin):
        """
        Register user credentials with PIN number 
        
        :param int pin: PIN number
        
        """
        uri = self.server + "/credentials/users/reset"
        uri += "?pin=" + str(pin)

        return self.request.get(uri, self.timeout)

    def get_groups(self, name_filter=None, key=None):
        """
        Get group credentials
        
        :param str filter: group name filter
        :param str key: group key  
        """
        uri = self.server + "/credentials/groups"
        if key:
            uri += "?key=" + str(key)
        elif name_filter:
            uri += "?filter=" + str(name_filter)

        return self.request.get(uri, self.timeout)

    def get_group_members(self, name_filter=None, key=None):
        """
        Get group credentials
        
        :param str filter: group name filter
        :param str key: group key  
        """
        uri = self.server + "/credentials/groups/members"
        if key:
            uri += "?key=" + str(key)
        elif name_filter:
            uri += "?filter=" + str(name_filter)

        return self.request.get(uri, self.timeout)

    def set_group(self, value):
        """
        Set group credentials 
        
        :param str value: group json data
        """
        uri = self.server + "/credentials/groups"

        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_group(self, name_filter, key=None):
        """
        Delete group credentials
        
        :param str filter: group name filter
        :param str key: group key       
        """
        uri = self.server + "/credentials/groups"
        if key:
            uri += "?key=" + str(key)
        elif name_filter:
            uri += "?filter=" + str(name_filter)

        return self.request.delete(uri, self.timeout)


class Device:
    """Represents an IoT Device in a cluster.

    :param server: a server object
    :param str device: name of the device returned by the get_device_list(),
                       such as 'device0' etc.
    :param bool unit: indicates if unit for params is to be fetched.
    :param bool advanced: fetches advanced params of the device if True
    :param bool development: fetches dev params of the device if True
    
    """

    def __init__(self, server, device, unit=True, advanced=False, development=False):
        self.server = server
        self.device = device.replace(" ", "_")
        self.unit = unit
        self.advanced = advanced
        self.development = development
        self.ts = None

        self.request = server.request

    def time(self):
        return self.ts

    def get(self, parameter='', after=None, options=False, attributes=None):
        """Retrieves one or more parameters of the device.
        If parameter is specified, then only that param info is fetched.
        Otherwise, all the params are fetched.
        A parameter can have a finite range of values, which can be fetched with ``options=True`` flag.

        :param str parameter: name of the parameter
        :param bool after: wait time?
        :param bool options: flag to determine if param options are to be fetched
        :param str attributes: fetches attributes of the passed value
        :returns: list of values
        :rtype: list
        :raises: HTTPError, socket.timeout
        """
        uri = self.server.server_url + "/"
        uri += self.device + "/"
        uri += parameter.replace('.', '/') + ".json"

        qp = []
        if self.unit:
            qp.append('unit=true')
        if after:
            qp.append('after=' + str(after))
        if self.advanced:
            qp.append('advanced=true')
        if self.development:
            qp.append('development=true')
        if options:
            qp.append('options=true')
        if attributes:
            qp.append('attributes=' + str(attributes))

        qs = '?' + '&'.join(qp) or ''
        uri += qs
        return self._parse_status(self.request.get(uri, self.server.timeout))

    def get_value(self, parameter, after=None):
        """Fetches value of the parameter from Device.

        :param str parameter: name of the parameter whose value is to be fetched
        :returns: value of the parameter
        :raises: HTTPError, socket.timeout
        """
        param = parameter.replace('.', '/')
        result = self.get(param, after)
        return result[param.split('/')[-1]]['value']

    def get_records(self, parameter, time_from=None, time_to='last',
                    limit=None, scale=None, average=None, calc=None, show=None):
        """Retrieves values from record storage.

        time_from provides filter value either as a UTC timestamp
        or as 'first' or 'start' strings to indicate that
        retrieval is to be made from first available record.

        time_to provides filter value either as a UTC timestamp
        or one of 'last' or 'end' strings to indicate that
        retrieval is to be made till last n=limit available records.

        Both scale and limit args limit the number of records being returned.
        However, limit returns records each containing ``N`` property.
        scale arg returns records, each containing ``M`` property.
        They are *mutually exclusive*; providing them both raises ``ValueError``
        with appropriate message.
        If none are provided, then server restricts the number of records by 100
        with each record containing ``N`` property by default.

        average arg can be used only with scale;
        providing average without scale raises ValueError.
        average specifies the number of records to be averaged on
        to determine a single scale value.
        average usage is hinted by ``SD`` property present in the response.

        :param str parameter: parameter name or stringified number
        :param int or str time_from: time from which records are to be fetched
        :param int or str time_to: time till which records are to be fetched
        :param int limit: max number of records to return with ``N`` property in each sample
        :param int scale: max number of records to return with ``M`` property in each sample
        :param int average: number of records to average on in case of scale

        :returns: list of JSON objects
        :rtype: list
        :raises: HTTPError, socket.timeout, ValueError
        """
        if limit and scale:
            raise ValueError('Provide either limit or scale arg. They are mutually exclusive.')
        if average and not scale:
            raise ValueError('average arg can only be used with scale arg.')

        uri = self.server.server_url + "/"
        uri += self.device + "/"
        uri += parameter.replace('.', '/') + ".json"

        qp = []
        if limit:
            qp.append('limit=' + str(limit))
        if scale:
            qp.append('scale=' + str(scale))
        if average:
            qp.append('average=' + str(average))
        if time_from:
            qp.append('from=' + str(time_from))
        if time_to:
            qp.append('to=' + str(time_to))
        if calc:
            qp.append('calc=' + str(calc))
        if show:
            qp.append('show=' + str(show))
        if self.advanced:
            qp.append('advanced=true')
        if self.development:
            qp.append('development=true')
        if self.unit:
            qp.append('unit=true')
        qs = '?' + '&'.join(qp) or ''
        uri += qs
        return self.request.get(uri, self.server.timeout)

    def get_args(self, msg):
        """
        Get arguments for given message
        """
        uri = self.server.server_url + "/" + self.device + "/" + str(msg)
        return self.request.get(uri, self.server.timeout)

    def set_args(self, msg, data):
        """
        Set arguments for given message
        """
        uri = self.server.server_url + "/" + self.device + "/" + str(msg)
        return self.request.post(uri, json.dumps(data), self.server.timeout)

    def set(self, parameter, data, after=None):
        """Set device variables

        :param str parameter: parameter name or stringified number
        :param str data: variable data in json format

        :returns: result of the set values in json format
        :raises: HTTPError, socket.timeout
        """
        uri = self.server.server_url + "/"
        uri += self.device + "/"
        uri += parameter.replace('.', '/')

        struct = data.copy()
        if after:
            struct["$after"] = after
        if self.advanced:
            struct['advanced'] = True
        if self.development:
            struct['development'] = True

        resp = self.request.post(uri, json.dumps(struct), self.server.timeout)
        return self._parse_status(resp)

    def set_value(self, parameter, data, after=None):
        param = parameter.replace('.', '/')
        result = self.get(param)
        token = param.split('/')[-1]
        result[token]['value'] = data
        result = self.set(param, result, after)
        try:
            return result[token]['value']
        except:
            return result['status']

    def query(self, parameter):
        """
        query given parameter
        :param parameter: 
        :return: 
        """
        return self.set(parameter, {})

    def get_device_status(self):
        """
        Get connected device status
        
       
        :returns: device status in json form
        """
        uri = self.server.server_url + "/" + self.device + "/device_status"

        return self.request.get(uri, self.server.timeout)

    def set_device_setting(self, data):
        """
        Set device parameter
                
        :param data: data format {"setting_name":"value"}
        :returns: operation result
        """
        uri = self.server.server_url + "/" + self.device + "/device_status"
        return self.request.post(uri, json.dumps(data), self.server.timeout)

    def _parse_status(self, result):

        if isinstance(result, list):
            return result

        # try:
        #    self.ts = float(result['time'])
        # except:
        #    print("Return struct is missing time specifier")

        status = 'OK'
        try:
            status = result['status']
        except:
            pass
            # print("Return struct is missing status")

        if status.upper() not in ['OK', 'ACK']:
            raise IOError(status)
        return result


class Parameter:
    """Represents a parameter of a device

    :param Device device: a device object
    :param str parameter: parameter name or stringified number
    """

    def __init__(self, device, parameter):
        self.device = device
        self.parameter = parameter.replace('.', '/')
        self.ts = 0
        self.lunit = None
        self.lvalue = None
        self.struct = self.get()
        param = self.parameter.split('/')[-1]  # Only the last parameter is of interest.

        for v in self.struct.keys():
            if param in v:
                self.key = v

    def time(self):
        return self.ts

    def value(self):
        return self.lvalue

    def unit(self):
        return self.lunit

    def get_value(self, after=None):
        value = self.get(after)
        return value[self.key]['value']

    def get_options(self):
        """Retrieves the list of possible values that the Parameter instance can possess.
        If such a range is defined, then it is returned else None is returned.

        :returns: list of option values else None
        """
        resp = self.get(options=True)
        return resp[self.key].get('options', None)

    def get(self, after=None, options=False, attributes=None):
        resp = self.device.get(self.parameter, after=after,
                               options=options, attributes=attributes)
        return self._parse_status(resp)

    def get_records(self, time_from=None, time_to='last',
                    limit=None, scale=None, average=None):
        resp = self.device.get_records(self.parameter,
                                       time_from=time_from, time_to=time_to,
                                       limit=limit, scale=scale, average=average)
        return self._parse_status(resp)

    def set_value(self, new_value, after=None):

        self.struct[self.key]['value'] = new_value
        self.set(self.struct, after)
        return self.value()

    def set(self, data, after=None):
        """Set values of a given parameter(s)

        :param str data: variable data in json format

        :returns: list of values
        :raises: HTTPError, socket.timeout
        """
        resp = self.device.set(self.parameter, data, after)
        return self._parse_status(resp)

    def query(self):
        """
        Send message query for given parameter
        :param data: 
        :return: 
        """
        resp = self.device.query(self.parameter)
        return self._parse_status(resp)

    def _parse_status(self, result):

        if isinstance(result, list):
            return result

        # try:
        #    self.ts = float(result['time'])
        # except:
        #    print("Return struct is missing time specifier")

        status = 'OK'
        try:
            status = result['status']
        except:
            pass
            # print("Return struct is missing status")

        if status.upper() not in ['OK', 'ACK']:
            raise IOError(status)

        try:
            self.lvalue = result[self.key]['value']
        except:
            self.lvalue = 'OK'

        try:
            self.lunit = result[self.key]['unit']
        except:
            self.lunit = None

        return result


class Service:
    """
    Represents active running service
    
    
    """

    def __init__(self, server, service):
        self.server = server
        self.service = service
        self.service_uri = self.server.server_url + "/services/" + service
        self.timeout = self.server.timeout
        self.request = server.request

    def stop(self):
        """
        Send stop signal to service
        """
        data = {"action": "stop"}

        return self.request.post(self.service_uri, json.dumps(data), self.timeout)

    def get_service_data(self, uri):
        """
        Get service data
        
        :param str uri: service uri
        """
        uri = self.service_uri + "/" + uri
        return self.request.get(uri, self.timeout)

    def post_service_data(self, uri, data):
        """
        Post service data
    
        :param str uri: service uri
        :param str data:
        """
        uri = self.service_uri + "/" + uri
        return self.request.post(uri, json.dumps(data), self.timeout)

    def get_service_property_list(self):
        """Retrieves a list of properties related to the service.
        :returns: list of property names
        :rtype: list
        """

        uri = self.service_uri + "/properties" + '.json'
        return self.request.get(uri, self.timeout)

    def get_service_property(self, prop, params=None):
        """Fetches value of *prop* property.
        The object returned has a definite structure:
        ``{ prop: {data: <value>}, time: <tstmp> }``

        :param str identifier: property group identifier
        :param str prop: name of the property
        :returns: value of the property
        :rtype: dict
        """
        prop = prop.replace(".", "/")

        uri = self.service_uri + "/properties/" + prop + '.json'

        uri = self.server.add_params_to_uri(uri, params=params)
        return self.request.get(uri, self.timeout)

    def set_service_property(self, prop, value, append=False):
        """Sets or overwrites the value of the *prop* property with *val* value.
        The *val* passed is stored and enclosed in:
        ``{prop: {data: <val>}}``

        :param str identifier: property group identifier
        :param str prop: name
        :param str|dict|number value: value
        :returns: result with structure ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")
        uri = self.service_uri + "/properties/" + prop + '.json'
        if append:
            uri += '?append=true'

        return self.request.post(uri, json.dumps(value), self.timeout)

    def delete_service_property(self, prop, params=None):
        """Deletes the `prop` property.
        The entire property, not only its value, is removed.
        
        :param str identifier: property group identifier
        :param str prop: name
        :return: response with structure: ``{result: Error|OK}``
        :rtype: dict
        """
        prop = prop.replace(".", "/")

        uri = self.service_uri + "/properties/" + prop + '.json'

        uri = self.server.add_params_to_uri(uri, params=params)
        return self.request.delete(uri, self.timeout)


# Example, accessing the Walnut and reading the system variables
if __name__ == "__main__":
    me = Group('http://localhost:9001', 'devices')
    print('Show available devices and pick up the first:')
    print(me.get_device_list())
    walnut = Device(me, me.get_device_list()[0]['name'])  # assume we have only walnut in the DB

    print('\nBoard was restarted:')
    print(walnut.get('walnut/sys/restarted'))  # show we can get values in this way

    reset = Parameter(walnut, 'walnut/sys/reset', False, 'ack')
    print('\nLast reset state:')
    print(reset.get_value())

    print('\nRestarting the board ...')
    print(reset.set_value('Reset'))

    print('\nNow board was restarted:')
    print(walnut.get('walnut/sys/restarted'))  # show we can get values in this way
