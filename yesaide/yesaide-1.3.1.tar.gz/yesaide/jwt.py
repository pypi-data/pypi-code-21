from jwcrypto.jwt import JWT, JWTExpired, JWTMissingKey
from jwcrypto.jws import InvalidJWSObject, InvalidJWSSignature


class JWTException(Exception):
    pass


class InvalidPayload(JWTException):
    pass


class InvalidSignature(JWTException):
    pass


class ExpiredToken(JWTException):
    pass


class MissingKey(JWTException):
    pass


def process_jwt_payload(payload, key):
    """Process a JWT payload (usually a string) and return a JWT object
    if the process went fine.

    """
    try:
        return JWT(
            key=key,
            jwt=payload,
            check_claims={'exp': None},  # Weird syntax but it says
                                         # "Check expiration time"
            algs=[
                'ES256', 'ES384', 'ES521',
                'RS256', 'RS384', 'RS512',
                'PS256', 'PS384', 'PS512',
            ],
        )
    except InvalidJWSObject:
        raise InvalidPayload()
    except JWTExpired:
        raise ExpiredToken()
    except JWTMissingKey:
        raise MissingKey()
    except InvalidJWSSignature:
        raise InvalidSignature()
