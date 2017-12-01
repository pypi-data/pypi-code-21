from restclients_core.exceptions import DataFailureException
from uw_coda.dao import CoDa_DAO
import json

DAO = CoDa_DAO()

API_BASE = "/api/v1/course/%s/"


def get_resource(url):
    response = DAO.getURL(url)

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)
    else:
        return json.loads(response.data)


def get_majors(section_label, num_majors):
    url = get_offering_url(section_label) + "/majors/" + str(num_majors)

    return get_resource(url)


def get_fail_rate(section_label):
    url = get_offering_url(section_label) + "/fail_rate"

    return get_resource(url)


def get_course_cgpa(section_label):
    url = get_offering_url(section_label) + "/cgpa"

    return get_resource(url)


def get_offering_url(section_label):
    return API_BASE % (section_label.replace(",", "-").replace("/", "-"))
