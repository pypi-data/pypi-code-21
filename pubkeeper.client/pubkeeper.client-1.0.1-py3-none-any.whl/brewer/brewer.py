"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.topic import Topic


class Brewer(Topic):
    def get_config(self):
        raise NotImplementedError()

    def new_patrons(self, patrons):
        raise NotImplementedError()

    def remove_patron(self, patron_id):
        raise NotImplementedError()

    def brew(self, data):
        raise NotImplementedError()
