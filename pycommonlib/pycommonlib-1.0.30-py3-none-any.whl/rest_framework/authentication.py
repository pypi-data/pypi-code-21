'''
Created on Dec 1, 2015

@author: panweif
'''
from rest_framework.authentication import TokenAuthentication
from common.util import datetime
from common.exceptions import TokenExpiredError


class ExpireableTokenAuthentication(TokenAuthentication):
    
    def authenticate_credentials(self, key):
        result = TokenAuthentication.authenticate_credentials(self, key)
        current = datetime.utc_now()
        if (current - result[1].created).total_seconds() > 86400:
            result[1].delete()
            raise TokenExpiredError()
        else:
            result[1].created = current
            result[1].save()
        return result
