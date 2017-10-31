from .AdditionalAddressFields import AdditionalAddressFields
from .AdditionalPersonFields import AdditionalPersonFields
from .AppendedFields import AppendedFields
from .Business import Business
from .Communication import Communication
from .DataFields import DataFields
from .DatasourceFields import DatasourceFields
from .DatasourceResult import DatasourceResult
from .Document import Document
from .DocumentTypes import DocumentTypes
from .DriverLicence import DriverLicence
from .Location import Location
from .NationalId import NationalId
from .NationalIdTypes import NationalIdTypes
from .Passport import Passport
from .PersonInfo import PersonInfo
from .Record import Record
from .RecordRule import RecordRule
from .RecordStatus import RecordStatus
from .ServiceError import ServiceError
from .VerifyRequest import VerifyRequest
from .VerifyResult import VerifyResult

from .client import Client as APIClient

__version__ = '0.1.0'


class Client:
    def __init__(self, base_uri="https://api.globaldatacompany.com"):
        self.api = APIClient(base_uri)
