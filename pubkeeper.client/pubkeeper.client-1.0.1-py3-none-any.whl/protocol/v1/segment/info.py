class SegmentInfo(object):
    """ Defines Segment information
    """
    def __init__(self,
                 previous_brewer_id, brewer, brewer_brew,
                 patron, patron_brew):
        # previous segment's brewer
        self.previous_brewer_id = previous_brewer_id
        self.brewer = brewer
        self.brewer_brew = brewer_brew
        self.patron = patron
        self.patron_brew = patron_brew
        # next segment's patron
        self.target_patron_id = None

    def __str__(self):  # pragma no cover
        return "previous_brewer_id: {}, brewer: {}, brewer_brew: {}" \
               "original_patron_id: {}, patron: {}, patron_brew: {}".\
            format(self.previous_brewer_id, self.brewer, self.brewer_brew,
                   self.target_patron_id, self.patron, self.patron_brew)
