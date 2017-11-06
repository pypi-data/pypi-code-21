import base64
import binascii
import json

from collections import Mapping
from six import text_type, binary_type

from craftai.errors import CraftAiTokenError

# Initial code retrieved from PyJWT
# cf. https://github.com/jpadilla/pyjwt/blob/ceff941/jwt/utils.py#L33-L42
def base64url_decode(base64_input):
  if isinstance(base64_input, text_type):
    base64_input = base64_input.encode("ascii")

  rem = len(base64_input) % 4

  if rem > 0:
    base64_input += b"=" * (4 - rem)

  return base64.urlsafe_b64decode(base64_input)

# Code inspired by PyJWT
# cf. https://github.com/jpadilla/pyjwt/blob/ceff941/jwt/api_jws.py#L144-L181
def jwt_decode(jwt):
  if isinstance(jwt, text_type):
    jwt = jwt.encode("utf-8")

  if not issubclass(type(jwt), binary_type):
    raise CraftAiTokenError("Invalid token type. Token must be a {0}".format(binary_type))

  try:
    signing_input, crypto_segment = jwt.rsplit(b".", 1)
    header_segment, payload_segment = signing_input.split(b".", 1)
  except ValueError:
    raise CraftAiTokenError("Not enough segments")

  try:
    header_data = base64url_decode(header_segment)
  except (TypeError, binascii.Error):
    raise CraftAiTokenError("Invalid header padding")

  try:
    header = json.loads(header_data.decode("utf-8"))
  except ValueError as e:
    raise CraftAiTokenError("Invalid header string: %s" % e)

  if not isinstance(header, Mapping):
    raise CraftAiTokenError("Invalid header string: must be a json object")

  try:
    payload_data = base64url_decode(payload_segment)
  except (TypeError, binascii.Error):
    raise CraftAiTokenError("Invalid payload padding")

  try:
    payload = json.loads(payload_data.decode("utf-8"))
  except ValueError as e:
    # Unable to load the payload as a json
    payload = payload_data

  try:
    signature = base64url_decode(crypto_segment)
  except (TypeError, binascii.Error):
    raise CraftAiTokenError("Invalid crypto padding")

  return (payload, signing_input, header, signature)
