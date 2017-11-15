"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""


class SegmentInfo(object):
    """ Defines Segment information
    """
    def __init__(self,
                 original_brewer_id, brewer, brewer_brew,
                 original_patron_id, patron, patron_brew):
        self.original_brewer_id = original_brewer_id
        self.brewer = brewer
        self.brewer_brew = brewer_brew
        self.original_patron_id = original_patron_id
        self.patron = patron
        self.patron_brew = patron_brew

    def __str__(self):  # pragma no cover
        return "original_brewer_id: {}, brewer: {}, brewer_brew: {}" \
               "original_patron_id: {}, patron: {}, patron_brew: {}".\
            format(self.original_brewer_id, self.brewer, self.brewer_brew,
                   self.original_patron_id, self.patron, self.patron_brew)
