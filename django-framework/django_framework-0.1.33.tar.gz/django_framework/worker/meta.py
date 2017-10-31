

from django_framework.django_helpers.meta_helpers.meta_registry import register_meta

from django_framework.django_helpers.meta_helpers import BaseMeta

class JobMeta(BaseMeta):
    
    ALLOWED_DEFAULT = []
    ALLOWED_ADMIN   = ['GET', 'POST', 'PUT']

    USER_ALLOWED_METHODS = ['GET','POST', 'PUT'] # this governs if the a specific user coming in Non-admin is allowed to perform actions
                                                 # ALLOWED_DEFAULT above, is used to determine if you are allowed to access it generically
                                                 # which in our case is no, unless you are admin

    DEFAULT_REQUIRE_AUTHENTICATION = True
    DEFAULT_ALLOWED_ACTIONS_UNAUTHENTICATED = []
    
    ADMIN_REQUIRE_AUTHENTICATION   = True
    
    
    @classmethod
    def allowed_method(cls, method, version = False, user_job = False):
        '''Based on the version (the type of endpoint coming in, /admin/ or not) 
        determine the allowed HTTP methods.
        '''
        
        if user_job == False and version == 'default' and method in cls.ALLOWED_DEFAULT:
            return True
        elif user_job == True and version == 'default' and method in cls.USER_ALLOWED_METHODS:
            return True
    
        if version == 'admin' and method in cls.ALLOWED_ADMIN:
            return True
        
        
        raise ValueError('The requested method does not work with this model!')
    
register_meta(JobMeta)
