from decimal import Decimal


class OwnershipMixin(object):

    @property
    def ownership(self):
        if hasattr(self, '_ownership'):
            return self._ownership

    @ownership.setter
    def ownership(self, ownership):
        """
        A list of dictionaries in format {'party_id': 'XYZ', 'split': Decimal('0.5')}
        :param ownership:
        :return:
        """
        error_msg = 'ownership must be a list of dictionaries'
        if ownership:
            if not isinstance(ownership, list):
                raise TypeError(error_msg)
            if not all([isinstance(item, dict) for item in ownership]):
                raise TypeError(error_msg)
            if not all([item.get('party_id') for item in ownership]):
                raise ValueError('Ownership missing one or more party_ids')
            if not all([item.get('split') for item in ownership]):
                raise ValueError('Ownership missing one or more splits')
            if sum([item.get('split') for item in ownership]) != Decimal('1'):
                raise ValueError('Ownership must sum up to 100%')
        self._ownership = ownership
