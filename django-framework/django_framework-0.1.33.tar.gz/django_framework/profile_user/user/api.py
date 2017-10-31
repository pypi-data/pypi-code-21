import arrow
import copy

from django.contrib.auth.models import User

# this is where we hold basic things
from django_framework.django_helpers.api_helpers import BaseAPI
from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer
from django_framework.django_helpers.exception_helpers.common_exceptions import LoginError


from django_framework.helpers.security_helpers import generate_unique_key, md5_hasher


#===============================================================================
# UserAPI
#===============================================================================
class UserAPI(BaseAPI):
    ProfileManager = get_manager(manager_name = 'profile')
    ProfileSerializer = get_serializer(serializer_name = 'profile', version = 'admin')
    
    UserManager = get_manager(manager_name = 'user')
    UserSerializer = get_serializer(serializer_name = 'user', version = 'admin')
    
    AuthTokenManager = get_manager(manager_name = 'auth_token')
    AdminAuthTokenSerializer = get_serializer(serializer_name = 'auth_token', version = 'admin')


    def __init__(self, **kwargs):
        kwargs['run'] = False
        
        self.model_name = 'Profile'
        
        kwargs['request_requires_authentication'] = False
        super(UserAPI, self).__init__(**kwargs)

    def register(self):
        
        #  VALIDATION the query_data must pass the serializer tests.  This validates the username.
        self.ProfileManager.validate(Serializer=self.ProfileSerializer, data=self.query_data) 
        
        # generate a username and password! then validate the password!
        user_data = {"username" : generate_unique_key(), "password" : self.query_data.get('password')}
        user_serializer = self.UserManager.validate(Serializer=self.UserSerializer, data=user_data)
        
        # CREATE the user.
        user = self.UserManager.create(Serializer=self.UserSerializer, data = user_serializer.validated_data)[0]

        data = copy.copy(self.query_data)
        data['user_id'] = user.id
        data['email'] =str(user.id)+'_auto@generated.com'  # we could just make it the username....

        # create the profile
        profile = self.ProfileManager.create(Serializer=self.ProfileSerializer, data=data)
        
        # create the associated token data
        auth_data = {'user_id' : user.id}
        auth_token = self.AuthTokenManager.create(Serializer=self.AdminAuthTokenSerializer, data=auth_data)[0]
        current_token = self.AuthTokenManager.get_auth_token(auth_token)
        
        self.set_response(response = [{"token" : str(current_token)}], response_type = 'token') # otherwise it's a UUID token
        
        
    def login(self):

        username = self.query_data.get('username')
        password = self.query_data.get('password')
        
        if not username: # we are missing username
            error_message = "Invalid username/password combination, please try again."
            raise LoginError(error_message)

        profile = self._get_profile_by_username(username = username)
        
        if password:
            self.authenticate_user_by_password(profile = profile, password = password)
            
        elif self.query_data.get("security_code"):
            self.authenticate_user_by_security_code(profile = profile, security_code = self.query_data.get("security_code"))
            
            self.update_password(new_password = self.query_data.get('new_password'))
        else:
            error_message = "Invalid username/password combination, please try again."
            raise LoginError(error_message)

        
        if self.query_data.get('override') != None and profile.user.is_staff == True:
            profile = self._get_profile_by_username(username = self.query_data.get('override'))
        
        
        # return the token!
        current_token = self._set_auth_token(profile = profile)
        self.set_response(response = [{"token" : str(current_token)}], response_type = 'token') # otherwise it's a UUID token
        return profile.user  # this is so we can deal with Django Login schema which sets sessions!
    
    
    def default_login(self):
        
        self.query_data = {'username' : 'test12', 'password' : 'test12'}
        
        return self.login()
    
    
    def logout(self):
        self.set_response(response = [{"success" : True}], response_type = 'logout')
        return
    
    def forgot_password(self):
        username = self.query_data.get('username')
        if not username:
            raise LoginError('You must provide a username.')
        profile = self._get_profile_by_username(username = username)
        
        objs, security_code = self.ProfileManager.set_security_code(profile = profile)
        
        self.set_response(response = [{"security_code" : str(security_code), 'message' : 'The code is valid until ' + str(objs[0].security_code_valid_until)}],response_type = 'security_code')
    
    def update_password(self):
        
        new_password = self.query_data.get('new_password')
        
        self.login() # we need to validate that this is a valid user, or at least sending all the correct information!
        
        self.UserManager.update()
        
        
        
    def update_username(self):
        pass
    
    
    def authenticate_user_by_security_code(self, profile, security_code, fail_silently = False):
        
        if profile.security_code == md5_hasher(security_code):
            if arrow.get(profile.security_code_valid_until) > arrow.utcnow():
                return True
            else:
                exception = LoginError('The security code you are using is no longer valid.  Please request a new one.')
            
        else:
            exception = LoginError('Invalid username/security code combination, please try again!')
        
        if fail_silently == False:
            raise exception
        return False
        
    def authenticate_user_by_password(self, profile, password, fail_silently = False):
        if profile.user.check_password(raw_password = md5_hasher(password)) == True:
            return True
        
        if fail_silently == False:
            raise LoginError('Invalid username/password combination, please try again!')
        return False
        

    
    
    def _get_profile_by_username(self, username):
        
        try:
            query_params = {"filter" : {"username": username}, 'select_related' : ['user']}
            profile = self.ProfileManager.get_by_query(query_params=query_params)[0]
        except:
            error_message = "Invalid username/password combination, please try again."
            raise LoginError(error_message)
        
        return profile
        
        
    def _set_auth_token(self, profile):
        '''Presumes validation already been done'''
        query_params = {"filter" : {"user_id": profile.user.id}}
        auth_token = self.AuthTokenManager.get_by_query(query_params=query_params)[0]
        
        # update the auth token if we need to.
        if auth_token.expire_at <= arrow.utcnow():
            auth_token = self.AuthTokenManager.refresh_token(model = auth_token)[0]
        
        current_token = self.AuthTokenManager.get_auth_token(auth_token = auth_token, profile = profile)
        
        return current_token
    
    
    def get_response(self):
        return self.response