import uuid
from os import path

import attr
from zeep import Client
from zeep.exceptions import Error
from zeep.wsse import UsernameToken

# I'm not a fan of the idea of fetching an API definition over HTTP just to
# initialize an API client.
DEFAULT_STUDENT_SERVICE_WSDL_URL = (
    f'file://{path.dirname(path.realpath(__file__))}/wsdl/StudentService_2.0_production.wsdl'
)
DEFAULT_STUDENT_SERVICE_PORT_NAME = 'BasicHttpBinding_IStudentService'

NOT_FOUND_MESSAGE = 'Could not find Student in database'


class StudentNotFound(Error):
    pass


@attr.s(frozen=True)
class Student:
    full_name = attr.ib()
    first_name = attr.ib(repr=False)
    last_name = attr.ib(repr=False)
    liu_id = attr.ib()
    email = attr.ib(repr=False)
    nor_edu_person_lin = attr.ib()
    liu_lin = attr.ib(repr=False)

    main_union = attr.ib(repr=False)
    student_union = attr.ib(repr=False)
    edu_person_affiliations = attr.ib(repr=False)
    edu_person_scoped_affiliations = attr.ib(repr=False)
    edu_person_primary_affiliation = attr.ib(repr=False)


@attr.s(frozen=True)
class StudentServiceClient:
    username = attr.ib()
    password = attr.ib(repr=False)

    wsdl_url = attr.ib(repr=False, default=DEFAULT_STUDENT_SERVICE_WSDL_URL)
    port_name = attr.ib(repr=False, default=DEFAULT_STUDENT_SERVICE_PORT_NAME)

    _zeep_client = attr.ib(init=False)

    @_zeep_client.default
    def init_zeep_client(self):
        return Client(
            wsdl=self.wsdl_url, port_name=self.port_name,
            wsse=UsernameToken(username=self.username, password=self.password)
        )

    def get_student(
        self,
        iso_id=None,
        liu_id=None,
        mifare_id=None,
        nor_edu_person_lin=None,
        nor_edu_person_nin=None
    ):
        # Removes leading zeros from card numbers
        if iso_id:
            iso_id = str(iso_id).lstrip('0')
        if mifare_id:
            mifare_id = str(mifare_id).lstrip('0')

        identity = dict(
            IsoNumber=iso_id,
            LiUId=liu_id,
            MifareNumber=mifare_id,
            norEduPersonLIN=nor_edu_person_lin,
            norEduPersonNIN=nor_edu_person_nin
        )

        try:
            response = self._zeep_client.service.GetStudent(dict(Identity=identity))
        except Error as exc:
            if NOT_FOUND_MESSAGE in exc.message:
                raise StudentNotFound(message=f'Student not found: {identity}') from exc
            raise exc

        return Student(
            full_name=response.DisplayName,
            first_name=response.GivenName,
            last_name=response.SurName,
            liu_id=response.LiUId,
            # Sesam sometimes responds with no email address.
            email=response.EmailAddress or f'{response.LiUId}@student.liu.se',
            nor_edu_person_lin=uuid.UUID(response.norEduPersonLIN),
            liu_lin=uuid.UUID(response.LiULIN),
            main_union=response.MainUnion,
            student_union=response.StudentUnion,
            edu_person_affiliations=frozenset(response.eduPersonAffiliations.string),
            edu_person_scoped_affiliations=frozenset(response.eduPersonScopedAffiliations.string),
            edu_person_primary_affiliation=response.eduPersonPrimaryAffiliation
        )
