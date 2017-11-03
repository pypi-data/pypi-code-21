

from django.contrib.auth.models import User
from django_framework.django_helpers.exception_helpers.common_exceptions import PermissionError, PermissionAdminError

def is_authenticated(user, require_admin = False): 
    
    if type(user) != User: # hmm we update this
        raise PermissionError('This endpoint requires you to be logged in.  You cannot access this.')

    if require_admin == True and user.is_staff != True:
        raise PermissionAdminError('You must be an admin user to access this endpoint.')
    
    return True