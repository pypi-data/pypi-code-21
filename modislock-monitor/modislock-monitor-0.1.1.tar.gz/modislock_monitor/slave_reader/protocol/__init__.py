"""
.. module:: key protocols
   :platform: Unix
   :synopsis: Protocols for each acceptable key algorithm is contained here.

.. moduleauthor:: Richard Lowe <richard@modislab.com>

"""

from .otp import OTPValidate
from .pin import PINValidate
from .rfid import RFIDValidate
from .totp import TOTPValidate
from .u2f import U2FValidate
from .validator import Validator

__all__ = ['OTPValidate', 'PINValidate', 'RFIDValidate', 'U2FValidate', 'TOTPValidate', 'Validator']
