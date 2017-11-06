from .AdditionalAddressFields import AdditionalAddressFields
from .AdditionalPersonFields import AdditionalPersonFields
from .AppendedField import AppendedField
from .Business import Business
from .Communication import Communication
from .CountrySubdivision import CountrySubdivision
from .DataFields import DataFields
from .DatasourceField import DatasourceField
from .DatasourceResult import DatasourceResult
from .Document import Document
from .DocumentTypes import DocumentTypes
from .DriverLicence import DriverLicence
from .Fields import Fields
from .InputField import InputField
from .Location import Location
from .NationalId import NationalId
from .NationalIdTypes import NationalIdTypes
from .Passport import Passport
from .PersonInfo import PersonInfo
from .Properties import Properties
from .PropertyType import PropertyType
from .Record import Record
from .RecordRule import RecordRule
from .RecordStatus import RecordStatus
from .ServiceError import ServiceError
from .TransactionRecordResult import TransactionRecordResult
from .VerifyRequest import VerifyRequest
from .VerifyResult import VerifyResult

from .client import Client as APIClient

__version__ = '0.6.0'


class Client:
    def __init__(self, base_uri="https://api.globaldatacompany.com"):
        self.api = APIClient(base_uri)
