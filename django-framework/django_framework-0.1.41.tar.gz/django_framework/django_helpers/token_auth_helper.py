#############################
#
#
#  Used to customize the user that is returned from cookie based authentication
#  as well as header based authentication
#
#
###############################

import json
import arrow
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from rest_framework import exceptions, HTTP_HEADER_ENCODING, authentication


from django_framework.helpers.security_helpers import decrypter

from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.cache_helpers import NormalCache

try:
    IS_AUTHENTICATION_SERVER = settings.IS_AUTHENTICATION_SERVER
except:
    IS_AUTHENTICATION_SERVER = False

try:
    AUTHENTICATION_SHOULD_PASSTHROUGH = settings.AUTHENTICATION_SHOULD_PASSTHROUGH
except:
    AUTHENTICATION_SHOULD_PASSTHROUGH = True

class TokenAuthentication(authentication.BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    """
    A custom token model may be used, but must have the following properties.
    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        '''Override from base class, required, needs to return a 2-tuple
        (User, astring)
        User needs to be a django derived class of User or AnonymousUser
        '''
        
        
        if request.META.get('HTTP_AUTHORIZATION', None):# authenticating via Headers
            response = self.authenticate_via_headers(request = request)
        
        elif request.COOKIES.get('AUTHORIZATIONID', None): # authenticating via cookies!
            response = self.authenticate_via_cookies(request = request)
            
        else:
            response = None
            
        if response == None:
            response = (self.create_anonymous_user(), 'anonymous_user')
        
        return response
    
    def authenticate_via_headers(self, request):
        print('whats going headers', request.META.get('HTTP_AUTHORIZATION'))
        '''Returns a (User, token) or None'''
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode(HTTP_HEADER_ENCODING)  # Work around django test client oddness
        auth = auth.split()  # split by spaces!

        print('split ', auth, len(auth))
        if not auth or auth[0].lower() != b'token':
            response = None
            
        elif len(auth) != 2:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        else:
            print('woah')
            response = self.authenticate_credentials(token=auth[1])
        return response
    
    def authenticate_via_cookies(self, request):
        '''Returns a (User, token) or None'''
        auth = request.COOKIES.get('AUTHORIZATIONID')
        if isinstance(auth, str):
            auth = auth.encode(HTTP_HEADER_ENCODING)  # Work around django test client oddness

        if not auth:
            response = None
        else:
            response = self.authenticate_credentials(token=auth)
        return response
    
    def authenticate_credentials(self, token):
        '''Validates that the token is correct and returns a User'''
        print('my token', token)
        # set up the default cookie login to be reading normal cookies
        is_logged_in = False
        user = None
        try:
            user = self._token_to_user(token = token)
            is_logged_in = True
        except Exception as e:
            print(e)
                

        # should default fail, and we do allow this special pass through then, try it.
        print('What the heck!', AUTHENTICATION_SHOULD_PASSTHROUGH)
        if is_logged_in == False and AUTHENTICATION_SHOULD_PASSTHROUGH == True:
            user = self._passthrough_to_user(token)
        

        # otherwise it passses! as we need to go get the user!
        if user is None:
            raise exceptions.AuthenticationFailed('Unable to validate based on token!')
        return (user, token)
    
    def _token_to_user(self, token):
        '''Wrapping the logic around a try except loop, otherwise checks if valid token
        and converts to user.'''
        try:
            user = self.convert_token_to_user(token = token)
            if IS_AUTHENTICATION_SERVER == True:
                self.verify_token(user_id = user.id, token = user.current_token)
                
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))
        
        return user
        
    def _passthrough_to_user(self, token):
        '''Excepts a properly formatted dictionary that has information already!'''
        if AUTHENTICATION_SHOULD_PASSTHROUGH == True:
            
            try:
                user = self.convert_passthrough_to_user(token = token)
            except Exception as e:
                raise exceptions.AuthenticationFailed(str(e))
        else:
            user = None
        return user
    
    def convert_passthrough_to_user(self, token):
        
        # this is only used to allow a direct pass through.  This is very
        # insecure as we are passing things in plain text as a dictionary
        token = json.loads(token)
        token['expire_at'] = arrow.utcnow().replace(days =+1)
        token['current_token'] = None
    
    
        return self.create_user(data = token)
    
    def convert_token_to_user(self, token):
        cache = self.get_cache(token)
        info_token=cache.get()

        if info_token == None:
            data = decrypter(astr = token, des_key = settings.PRIVATE_TRIPLE_DES_TOKEN_KEY)
            info_token = json.loads(data)
            cache.set(value = info_token, ttl = 300)
            
        
        return self.create_user(data = info_token)
    
    def create_user(self, data):
        '''Create a django User (we never save it. ever!)
        Additional fields are added to make it convenient to use in the rest of the framework.
        '''
        user = User()
        user.id = data['user_id']
        user.is_staff = data['user_is_staff']
        
        user.profile_id = data['profile_id']
        user.profile_uuid = data['profile_uuid']
        
        user.expire_at = data['expire_at']
        user.current_token = data['current_token']
        return user

    def create_anonymous_user(self):
        '''Create a django AnonymousUser (we never save it. ever!)
        Additional fields are added to make it convenient to use in the rest of the framework.
        '''
        user = AnonymousUser()
        user.id = -1
        user.is_staff = False
        
        user.profile_id = -1
        user.profile_uuid = 'anonymous_user'
        user.expire_at = None
        user.current_token = None
        
        
        return user


    def verify_token(self, user_id, token):
        user = get_manager('AuthToken').authenticate(user_id=user_id, token = token)
        if user == None:
            raise exceptions.AuthenticationFailed('Please check token and try again.  Typically expired tokens!')
    
    
    def get_cache(self, key):
        return NormalCache(key = key)