
class BaseMeta(object):
    
    ALLOWED_DEFAULT = None  # A list of request.methods allows for non-admin users.  ex: ['GET', 'PUT', 'POST', 'DELETE']
    ALLOWED_ADMIN   = None  # A list of request.methods for admin users, accessible via the  /admin/ endpoints ex: ['GET', 'PUT', 'POST', 'DELETE']


    # note that settings in here will override ALLOWED_DEFAULT!
    DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED = [] # if not authenticated, what methods are allowed? -- typically ['GET']


    DEFAULT_REQUIRE_AUTHENTICATION = True # do you need to be an authenticated user to view anything?  # this is same as setting DEFAULT_ACTIONS_AUTHENTICATED = ['GET']
    ADMIN_REQUIRE_AUTHENTICATION   = True # do admin endpoints require authentication, typically True!
    
    @classmethod
    def allowed_method(cls, method, version = False):
        '''Based on the version (the type of endpoint coming in, /admin/ or not) 
        determine the allowed HTTP methods.
        '''
        
        if version == 'default' and method in cls.ALLOWED_DEFAULT:
            return True
        
        if version == 'admin' and method in cls.ALLOWED_ADMIN:
            return True
        
        
        if version == 'default' and method in cls.DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED:
            return True
        
        raise ValueError('The requested method does not work with this model!')

        