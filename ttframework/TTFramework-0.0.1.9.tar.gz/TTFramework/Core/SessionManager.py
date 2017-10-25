from .DatetimePlus import DatetimePlus
from .Encryption import Encryption


class SessionManager(object):
    _users_session = {}
    _users_last_process_time = {}
    def __init__(self):
        pass

    def get_request_unique_info(self,request):
        host = request.remote_addr
        user_agent = request.headers.get('User-Agent',None)
        if user_agent and host:
            return Encryption.encrypt_md5_by_str(host + user_agent)
        return None

    def create_user_session(self,unique_info):
        self._users_last_process_time[unique_info] = DatetimePlus.get_now_datetime()
        self._users_session[unique_info] = {}
        return self._users_session[unique_info]

    def update_session_state(self,unique_info):
        if self._users_last_process_time.get(unique_info,None):
            self._users_last_process_time[unique_info] = DatetimePlus.get_now_datetime()

    def remove_timeout_session(self):
        _now_time = DatetimePlus.get_now_datetime()
        for _name in self._users_session.keys():
            if DatetimePlus.get_diff_minutes(_now_time,self._users_last_process_time[_name]) > 10:
                try:
                    self._users_session.pop(_name)
                except:
                    pass
                try:
                    self._users_last_process_time.pop(_name)
                except:
                    pass


    def get_session(self,request):
        _unique_info = self.get_request_unique_info(request)
        self.update_session_state(_unique_info)
        if _unique_info:
            result = self._users_session.get(_unique_info,None)
            if not result:
                result = self.create_user_session(_unique_info)
            return result
        return {}

    def set_session(self,request,value):
        _unique_info = self.get_request_unique_info(request)
        if _unique_info:
            self._users_session[_unique_info] = value
            self._users_last_process_time[_unique_info] = DatetimePlus.get_now_datetime()