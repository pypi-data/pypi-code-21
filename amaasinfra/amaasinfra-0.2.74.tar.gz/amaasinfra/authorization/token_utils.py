import os
from enum import Enum
from typing import Dict
import jwt

class TokenAttribute(Enum):
    first_name = 'given_name'
    last_name = 'family_name'
    email = 'email'
    username = 'cognito:username'
    asset_manager_id = 'custom:asset_manager_id'

def unpack_token(token: str) -> Dict[str, str]:
    """
    Unpacks the Cognito token attributes into a list of their values.
    
    Args:
        token: the encoded jwt token from the Authorization request header
        *additional_attributes: optional token attributes to be unpacked and returned
    
    Returns:
        Dict[TokenAttribute, str]: the list containing the attribute values
    """
    contents = jwt.decode(token, verify=False)
    return {attr.value: contents.get(attr.value, None) for attr in TokenAttribute}
