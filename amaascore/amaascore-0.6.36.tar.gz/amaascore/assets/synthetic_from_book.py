from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import date

from amaascore.assets.synthetic import Synthetic


class SyntheticFromBook(Synthetic):
    """ A synthetic asset whose value is based on the value of the assets in a referenced book """

    def __init__(self, asset_id, asset_manager_id, book_id=None, asset_issuer_id=None, asset_status='Active',
                 country_id=None, currency=None, display_name='', description='', fungible=True, issue_date=date.min,
                 maturity_date=date.max, comments=None, links=None, references=None, *args, **kwargs):
        self.book_id = book_id
        super(SyntheticFromBook, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                fungible=fungible, asset_issuer_id=asset_issuer_id,
                                                asset_status=asset_status, currency=currency,
                                                issue_date=issue_date, maturity_date=maturity_date,
                                                country_id=country_id, roll_price=False,
                                                display_name=display_name, description=description,
                                                comments=comments, links=links, references=references,
                                                *args, **kwargs)
