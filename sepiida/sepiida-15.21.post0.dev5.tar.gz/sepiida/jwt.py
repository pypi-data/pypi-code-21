import hashlib
import json as JSON
import logging
from datetime import datetime, timedelta

import jwt
from flask import current_app, g, request

from sepiida.errors import APIException, Error
from sepiida.requests import privileged_session

LOGGER = logging.getLogger(__name__)

ALGORITHM = 'RS512'

def register_jwt_handlers(app, secret_key=None, secret_key_path=None):
    app.config['SEPIIDA_JWT_KEY'] = secret_key or read_secret_key(secret_key_path)
    app.before_request(jwt_handler)

def jwt_handler():
    _jwt = request.headers.get('jwt')
    if _jwt:
        try:
            g.jwt = validate(_jwt)
        except Error as e:
            raise APIException(errors=[e])

def request_jwt():
    return g.get('jwt', None)

def validate(token, payload=None, audience=None):
    iss = decode_iss(token)
    session = privileged_session()
    response = session.get(iss, timeout=5)
    if not response.ok:
        LOGGER.warning('Issuer (%s) request failed with status code %s: %s', iss, response.status_code, response.text)
        raise InvalidIssuerError("jwt-invalid-issuer", "Invalid issuer")

    response_json = response.json()
    if not response_json:
        raise InvalidIssuerError("jwt-invalid-issuer-response", "Invalid issuer response")

    secret = response_json.get('secret')
    if not secret:
        LOGGER.warning('Issuer (%s) request failed with missing secret token', iss)
        raise InvalidIssuerError("jwt-invalid-issuer-secret", "Invalid issuer secret")

    if not audience:
        audience = request.url_root

    if not payload:
        payload = request.get_data()

    return decode(token, cert=secret, payload=payload, audience=audience)

def decode(token, cert=None, payload=None, verify=True, audience=None, issuer=None):
    options = {
        "require_exp": True,
        "require_iat": True,
        "require_nbf": True,
    }

    try:
        body = jwt.decode(token, cert, options=options, verify=verify, audience=audience, issuer=issuer, leeway=10)
    except jwt.exceptions.MissingRequiredClaimError as ex:
        LOGGER.warning(ex)
        raise MissingClaimError("jwt-missing-claim", str(ex))
    except jwt.exceptions.InvalidIssuerError as ex:
        LOGGER.warning(ex)
        raise InvalidIssuerError("jwt-invalid-issuer", str(ex))
    except jwt.exceptions.InvalidAudienceError as ex:
        LOGGER.warning(ex)
        raise InvalidAudienceError("jwt-invalid-audience", str(ex))
    except jwt.exceptions.ExpiredSignatureError as ex:
        LOGGER.warning(ex)
        raise ExpiredSignatureError("jwt-signature-expired", str(ex))
    except jwt.exceptions.DecodeError as ex:
        LOGGER.warning(ex)
        raise DecodeError("jwt-decode-error", str(ex))

    if "exp" in body:
        body["exp"] = datetime.utcfromtimestamp(body["exp"])

    if "iat" in body:
        body["iat"] = datetime.utcfromtimestamp(body["iat"])

    if "nbf" in body:
        body["nbf"] = datetime.utcfromtimestamp(body["nbf"])

    if not verify:
        return body

    if "bdy" in body:
        bdy = body["bdy"]
        expected_bdy = _encode_payload(payload)
        if bdy != expected_bdy:
            LOGGER.warning('Invalid bdy claim: bdy "%s" does not match payload "%s"', bdy, expected_bdy)
            raise InvalidBodyError("jwt-invalid-body", 'Invalid Body')

    return body

def encode(key=None, **kwargs):
    utcnow = datetime.utcnow()
    key = key if key else current_app.config.get('SEPIIDA_JWT_KEY')
    body = kwargs.copy()

    if "issuer" in body:
        body["iss"] = body.pop("issuer")

    if "subject" in body:
        body["sub"] = body.pop("subject")

    if "audience" in body:
        body["aud"] = body.pop("audience")

    if "exp" not in body:
        body["exp"] = utcnow + timedelta(seconds=900)

    if "iat" not in body:
        body["iat"] = utcnow

    if "nbf" not in body:
        body["nbf"] = utcnow

    payload = body.pop("payload", None)
    if payload:
        body["bdy"] = _encode_payload(payload)

    return jwt.encode(body, key, algorithm=ALGORITHM)

def decode_iss(token):
    body = decode(token, None, None, verify=False)
    iss = body.get("iss")
    if not iss:
        raise MissingClaimError("jwt-missing-cliam", 'Token is missing the "iss" claim')
    return iss

def read_secret_key(path=None):
    with open(path or "/etc/authentise/authentise.jwt.key.pem") as f:
        return f.read()

def _encode_payload(payload):
    if isinstance(payload, dict):
        payload = JSON.dumps(payload).encode()
    elif isinstance(payload, str):
        payload = payload.encode()
    return hashlib.sha256(payload).hexdigest()

class DecodeError(Error):
    pass

class InvalidClaimError(Error):
    pass

class MissingClaimError(Error):
    pass

class InvalidIssuerError(Error):
    pass

class InvalidAudienceError(Error):
    pass

class InvalidBodyError(Error):
    pass

class ExpiredSignatureError(Error):
    pass
