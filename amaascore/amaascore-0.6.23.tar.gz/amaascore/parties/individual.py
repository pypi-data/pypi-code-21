from __future__ import absolute_import, division, print_function, unicode_literals

from dateutil.parser import parse
import sys

from amaascore.parties.party import Party

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class Individual(Party):

    def __init__(self, asset_manager_id, party_id, given_names='', surname='', date_of_birth=None, base_currency=None,
                 party_status='Active', description=None, url='', 
                 addresses=None, comments=None, emails=None, links=None, references=None, *args, **kwargs):
        if not hasattr(self, 'party_class'):  # A more specific child class may have already set this
            self.party_class = 'Individual'
        self.given_names = given_names
        self.surname = surname
        self.date_of_birth = date_of_birth
        description = description or '%s, %s' % (self.surname, self.given_names)
        super(Individual, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                         base_currency=base_currency, party_status=party_status,
                                         description=description, url=url,
                                         addresses=addresses, comments=comments, emails=emails,
                                         links=links, references=references,
                                         *args, **kwargs)

    @property
    def date_of_birth(self):
        if hasattr(self, '_date_of_birth'):
            return self._date_of_birth

    @date_of_birth.setter
    def date_of_birth(self, value):
        """
        The date of birth of the individual.
        :param value:
        :return:
        """
        if value:
            self._date_of_birth = parse(value).date() if isinstance(value, type_check) else value
