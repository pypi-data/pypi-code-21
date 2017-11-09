
import copy
import arrow
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from django_framework.django_helpers.model_helpers import get_model_clean_name

from api_cache_mixin import APICacheMixin

from widgets import query_params_to_dict
from widgets.permission_helpers import is_authenticated

DEFAULT_PAGE_NUMBER = 1
DEFAULT_SHOW_NUMBER = 10

try:
    DEFAULT_SHOW_NUMBER = int(settings.DEFAULT_SHOW_NUMBER)
except Exception as e:
    print('There was an issue setting the Default Show Number, it has been reverted to default.', e)
    DEFAULT_SHOW_NUMBER = 10

class BaseAPI(APICacheMixin):
    '''Base API that most API's will inherit from.  Does some basic functionality.'''

    DEFAULT_PAGE_NUMBER = DEFAULT_PAGE_NUMBER
    DEFAULT_SHOW_NUMBER = DEFAULT_SHOW_NUMBER

    DEFAULT_FORMAT = 'json'
    
    def __init__(self, request, admin = False, **kwargs):
        super(BaseAPI, self).__init__()
        
        self.kwargs = kwargs
        
        self.request = request
        self.request_method = request.method  # GET, PUT, POST, DELETE, etc
        self.request_headers = request.META  # this is where Django RestFramework stores all the headers!
        
        self.request_is_authenticated = False # is the request authenticated?  Does not answer if the request NEEDS to be authenticated.
        self.request_requires_authentication = True # this determines if it requires Authentication.
        
        self.user = self.request.user  # provided from django or anon user

        self.admin = admin # True/False, if it is admin endpoint
        if self.admin == True:
            self.version = 'admin'
        else:
            self.version = 'default'
        
        # needs to be run after admin is set!
        self.request_requires_authentication = self.kwargs.get('request_requires_authentication', True)
        if self.request_requires_authentication == True:
            self.is_user_authenticated()
            
        
        # these must come after authentication and requests checking
        self.query_params = self._set_query_params()  
        self.query_data  = self._set_query_data()
        
        # this must come after query_params are set
        self._set_pagination()  # once responses are returned, will slice results to limit returns!

    def is_user_authenticated(self):
        '''Will raise an error if user is not authenticated or not authenticated as admin when required.'''
        is_authenticated(self.user, require_admin = self.admin) # considering moving this up...
        self.request_is_authenticated = True

    
    def get_request_header(self, key, http_append = True, fail_silently = True):
        '''Django Rest framework and probaly most web frameworks append an HTTP to the front.  This makes it easier to deal with.'''
        key = str(key).upper()  # captilize everything
        key = key.replace('-', '_') # replace all hyphens with underscores
        
        value = self.request_headers.get(key, 'does_not_exist') 
        if value == 'does_not_exist' and http_append == True:
            key = 'HTTP_' + key
            value = self.request_headers.get(key, 'does_not_exist') 
            
        if value != 'does_not_exist':
            return value
        elif fail_silently == False:
            raise ValueError('The header requested was not found and is required to proceed.' + str(key))
        
        return None

    
    def clean_model_name(self, model_name):
        return get_model_clean_name(model_name = model_name)

    def _paginate(self, data):
        
        start_index = self.page_show * (self.page_number - 1)
        end_index   = self.page_show * (self.page_number)
        
        return data[start_index : end_index]
        
        
    def set_response(self, response, response_type = None):
        meta_data = { "total_query_results" : len(response),
                      "type" : response_type,
                      "request_time" : arrow.utcnow().timestamp,
                      "request_time_alt" : arrow.utcnow().format('YYYY-MM-DD HH:mm:ss'),
                     }
        self.response = dict(data=response, meta_data = meta_data)
        
        
    def get_response(self, model = True):
        return self.response
    
    def serialize_data(self, data):
        return self.Serializer(self._paginate(data), many=True).data

    def should_use_cache(self):
        
        
        should_use_cache = True
        if self.get_request_header(key = 'Cache-Control', http_append = True, fail_silently = True) == 'no-cache':
            should_use_cache =  False
        
        return should_use_cache
    
    

    def _set_query_params(self):
        '''Read the query params from url request.
        reading raw from QUERY_STRING because previous versions did not correctly format things like:
        filter[id]=1&filter[created_at__gte]=12322, it would lump them together and you would lose one of the queries.
        '''
        params = query_params_to_dict(query_string = self.request.META.get("QUERY_STRING"))
        self.format = params.pop('format', None) # format is not a proper filter query for later...
        return params
    
    def _set_query_data(self):
        '''Set the POST/PUT data that will be used.  To prevent people from 
        adding things to other people's accounts (even though they would not be able to view it after)
        we stick in the requester's profile_uuid and profile_id.  Admin's are excepted.
        '''
        data = copy.copy(self.request.data)
        if data == None:
            data = {}
        if self.version == 'default':
            # we enforce that all data for PUT and POST MUST have 
            # the profile_uuid and profile_id!  This way users cannot spoof other people's accounts
            if type(self.user) == AnonymousUser:
                pass
            else:
                data['profile_id'] = self.user.profile_id
                data['profile_uuid'] = self.user.profile_uuid
                
        
        return data

    def _set_pagination(self):
        '''if these are set: 'page' is in format: {"number" : 1, "show" : 10}
        where number is the page number they are request and show is how many to return.
        
        number = 2 and show = 100
        would return (if there are that many) entries 100-200
         '''
        page = self.query_params.pop('page', {})
        # setting page, show and format should be taken out!
        # {"number" : 1, "show" : 10}  # mainly used in conjuction with GETS
            
        self.page_number = int(page.get('number', self.DEFAULT_PAGE_NUMBER))
        self.page_show = int(page.get('show', self.DEFAULT_SHOW_NUMBER))
        if self.page_number <= 0 or self.page_show <= 0:
            raise IOError('You cannot have a pagination with negative numbers or zeros.  number starts with 1.')

