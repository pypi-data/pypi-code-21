from __future__ import absolute_import, division, print_function, unicode_literals


class Portfolio(object):
    """
    TODO - does this derive from anything?  Sort of depends on whether or not we are planning on storing it.
    """

    def __init__(self, books=None):
        self.books = books

    def positions_by_book(self):
        """
        A dictionary of Position objects keyed by book_id.
        :return:
        """
        positions = None
        for book in self.books():
            positions[book] = book.positions()

    def positions_by_asset(self):
        """
        A dictionary of Position objects keyed by asset_id.  If an asset position exists in more than one book, they
         are combined into a single position.
        :return:
        """
        positions = None
        for book in self.books():
            book_positions = book.positions_by_asset()
            # unique positions
            positions.update({position.asset_id: position for position in book_positions
                              if position.asset_id not in positions.keys()})
            # Existing positions
            keys = [position.asset_id for position in book_positions if position.asset_id in positions.key()]
            for key in keys:
                positions.get(key).quantity += book_positions.get(key).quantity
        return positions
