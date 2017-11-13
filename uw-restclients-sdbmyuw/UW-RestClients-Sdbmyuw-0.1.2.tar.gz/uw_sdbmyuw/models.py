import json
import re
from restclients_core import models


class ApplicationStatus(models.Model):
    is_seattle = models.BooleanField(default=False)
    is_bothell = models.BooleanField(default=False)
    is_tacoma = models.BooleanField(default=False)
    no_ug_app = models.BooleanField(default=False)
    is_freshman = models.BooleanField(default=False)
    is_returning = models.BooleanField(default=False)
    is_post_bac = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    is_transfer = models.BooleanField(default=False)
    is_ug_non_matriculated = models.BooleanField(default=False)
    quarter = models.CharField(max_length=16, null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)

    def json_data(self):
        data = {
            'is_seattle': self.is_seattle,
            'is_bothell': self.is_bothell,
            'is_tacoma': self.is_tacoma,
            'no_ug_app': self.no_ug_app,
            'is_freshman': self.is_freshman,
            'is_international': self.is_international,
            'is_post_bac': self.is_post_bac,
            'is_returning': self.is_returning,
            'is_transfer': self.is_transfer,
            'is_ug_non_matriculated': self.is_ug_non_matriculated,
            'quarter': self.quarter,
            'year': self.year
        }

        if data['is_freshman']:
            data['type'] = "Freshman"
        elif data['is_post_bac']:
            data['type'] = "Postbaccalaureate"
        elif data['is_ug_non_matriculated']:
            data['type'] = "Nonmatriculated"
        elif data['is_transfer']:
            data['type'] = "Transfer"

        if 'type' in data and data['is_international']:
            data['type'] = "International " + data['type']

        return data

    def __str__(self):
        return json.dumps(self.json_data())


NO_UG_APP = re.compile(
    'The UW does not have an active undergraduate ' +
    'application on file for you.',
    re.I)


def has_no_ug_app(text):
    return re.search(NO_UG_APP, text) is not None


RETURN_PATTERN =\
    re.compile('returning student application to the UW ([BST][a-z]+),', re.I)
APP_PATTERN = re.compile(
    '>([ A-Za-z]+) application: ([a-z]+) quarter (\d{4})', re.I)
FRESHMAN = "freshman"
INTERNATIONAL = "international"
POST_BAC = "postbaccalaureate"
TRANSFER = "transfer"
UNDERGRADUATE_NON_MATRICULATED = "nonmatriculated"


def parse_statuses(html_data):

    if has_no_ug_app(html_data):
        status = ApplicationStatus()
        status.no_ug_app = True
        return [status]

    matched = re.search(RETURN_PATTERN, html_data)
    if matched is not None:
        status = ApplicationStatus()
        status.is_returning = True
        set_campus(status, html_data)
        return [status]

    match_tuples = []

    for m in re.finditer(CAMPUS_PATTERN, html_data):
        match_tuples.append((m.start(), m.group()))

    statuses = []
    for i in range(0, len(match_tuples)):
        status = ApplicationStatus()
        set_campus(status, match_tuples[i][1])

        start = match_tuples[i][0]
        end = (len(html_data) if i == len(match_tuples) - 1
               else match_tuples[i + 1][0])

        application_data = html_data[start:end]

        matched_str = re.search(APP_PATTERN, application_data)
        if matched_str is not None:
            if matched_str.group(1) is not None:
                apptype = matched_str.group(1).lower()

                if FRESHMAN in apptype:
                    status.is_freshman = True

                if POST_BAC in apptype:
                    status.is_post_bac = True

                if TRANSFER in apptype:
                    status.is_transfer = True

                if UNDERGRADUATE_NON_MATRICULATED in apptype:
                    status.is_ug_non_matriculated = True

                if INTERNATIONAL in apptype:
                    status.is_international = True

            if matched_str.group(2) is not None:
                status.quarter = matched_str.group(2).lower()

            if matched_str.group(3) is not None:
                status.year = int(matched_str.group(3))

        statuses.append(status)

    return statuses


CAMPUS_PATTERN = re.compile('<b>UW [BST][a-z]+ Campus Applications:</b>')
BOT = "Bothell"
SEA = "Seattle"
TAC = "Tacoma"


def set_campus(status, data):
    if SEA in data:
        status.is_seattle = True
    if BOT in data:
        status.is_bothell = True
    if TAC in data:
        status.is_tacoma = True
