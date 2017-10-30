from mongoframes import *
from mongoframes.frames import _FrameMeta
from datetime import date

from manhattan.comparable.change_log import ChangeLogEntry

__all__ = ['ComparableFrame']


class _ComparableFrameMeta(_FrameMeta):
    """
    Meta class for `ComparableFrame`s to ensure that `created` and `modified`
    are present in any defined set of fields (along with `_id`).
    """

    def __new__(meta, name, bases, dct):

        # If a set of fields is defined ensure it contains `created` and
        # `modified`.
        if '_fields' in dct:
            if not 'created' in dct['_fields']:
                dct['_fields'].update({'created'})

            if not 'modified' in dct['_fields']:
                dct['_fields'].update({'modified'})

        return super(_ComparableFrameMeta, meta).__new__(meta, name, bases, dct)


class ComparableFrame(Frame, metaclass=_ComparableFrameMeta):
    """
    A Frame-like base class that provides support for tracking changes to
    documents.

    Some important rules for creating comparable frames:

    - Override the `__str__` method of the class to return a human friendly
      identity as this method is called when generating a sticky label for the
      class.
    - Define which fields are references and which `Frame` class they reference
      in the `_compared_refs` dictionary if you don't you'll only be able to see
      that the ID has changed there will be nothing human identifiable.
    """

    # The class that will be used to store changes
    _change_log_cls = ChangeLogEntry

    # A set of fields that should be exluded from comparisons/tracking
    _uncompared_fields = {'_id', 'created', 'modified'}

    # A map of reference fields and the frames they reference
    _compared_refs = {}

    @property
    def comparable(self):
        """Return a dictionary that can be compared"""
        document_dict = self.compare_safe(self._document)

        # Remove uncompared fields
        self._remove_keys(document_dict, self._uncompared_fields)

        # Remove any empty values
        clean_document_dict = {}
        for k, v in document_dict.items():
            if not v and not isinstance(v, (int, float)):
                continue
            clean_document_dict[k] = v

        # Convert any referenced fields to Frames
        for ref_field, ref_cls in self._compared_refs.items():
            ref = getattr(self, ref_field)
            if not ref:
                continue

            # Check for fields which contain a list of references
            if isinstance(ref, list):
                if isinstance(ref[0], Frame):
                    continue

                # Dereference the list of reference IDs (retaining the order)
                docs = ref_cls.many(In(Q._id, ref))
                docs_map = {d._id: d for d in docs}
                docs = [docs_map[id] for id in ref if id in docs_map]
                clean_document_dict[ref_field] = docs

            else:
                if isinstance(ref, Frame):
                    continue

                # Dereference the reference ID
                clean_document_dict[ref_field] = ref_cls.by_id(ref)

        return clean_document_dict

    def logged_delete(self, user):
        """Delete the document and log the event in the change log"""

        # Dete the frame's document
        self.delete()

        # Log the change
        entry = self.__class__._change_log_cls({
            'type': 'DELETED',
            'documents': [self],
            'user': user
            })
        entry.insert()

        return entry

    def logged_insert(self, user):
        """Create and insert the document and log the event in the change log"""

        # Timestamp
        Frame.timestamp_insert(self, [self])

        # Insert the frame's document
        self.insert()

        # Log the insert
        entry = self.__class__._change_log_cls({
            'type': 'ADDED',
            'documents': [self],
            'user': user
            })
        entry.insert()

        return entry

    def logged_update(self, user, data, *fields):
        """
        Update the document with the dictionary of data provided and log the
        event in the change log.
        """

        # Get a copy of the frames comparable data before the update
        original = self.comparable

        # Update the frame
        _fields = fields
        if len(fields) == 0:
             _fields = data.keys()

        for field in _fields:
            if field in data:
                setattr(self, field, data[field])

        # Timestamp
        Frame.timestamp_update(self, [self])

        self.update(*fields)

        # Create an entry and perform a diff
        entry = self.__class__._change_log_cls({
            'type': 'UPDATED',
            'documents': [self],
            'user': user
            })
        entry.add_diff(original, self.comparable)

        # Check there's a change to apply/log
        if not entry.is_diff:
            return
        entry.insert()

        return entry

    @classmethod
    def compare_safe(cls, value):
        """Return a value that can be safely compared"""

        # Date
        if type(value) == date:
            return str(value)

        # Lists
        elif isinstance(value, (list, tuple)):
            return [cls.compare_safe(v) for v in value]

        # Dictionaries
        elif isinstance(value, dict):
            return {k: cls.compare_safe(v) for k, v in value.items()}

        return value
