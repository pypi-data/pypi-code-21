""" Reference field
"""
from persistent.list import PersistentList

from Products.validation import ValidationChain
from Products.Archetypes.atapi import ReferenceField

class EEAReferenceField(ReferenceField):
    """ Customize ReferenceBrowser field
    """
    _properties = ReferenceField._properties.copy()
    _properties.update({
        'edit_accessor': 'getRawRelatedItems'
    })

    def validate_relations(self, value, instance, errors=None, **kwargs):
        """ Validate relations
        """
        chainname = 'Validator_%s' % self.getName()
        validators = ValidationChain(chainname,
                                     validators=('eea.relations.required',))
        result = validators(value, instance=instance,
                            errors=errors, field=self, **kwargs)
        if result is not True:
            return result
        return None

    def validate(self, value, instance, errors=None, **kwargs):
        """ Validate passed-in value using all field validators.
            Return None if all validations pass; otherwise, return failed
            result returned by validator
        """
        if errors is None:
            errors = {}
        res = self.validate_relations(value, instance, errors, **kwargs)
        if res is not None:
            return res
        return super(EEAReferenceField, self).validate(
            value, instance, errors=None, **kwargs)

    def set(self, instance, value, **kwargs):
        """ On set, save the relations in the eea_refs attribute
        """
        # 30288 value needs to be a list of values and not a single object
        # for situations where only one relation is added
        if not isinstance(value, list):
            t = value
            value = []
            value.append(t)

        # 30398 for versioning, when versioning is used the values for related
        # items are not uids, but the objects, so we get their uid
        uid_value = []
        for val in value:
            if not isinstance(val, basestring):
                val = val.UID()
            uid_value.append(val)

        instance.eea_refs = PersistentList(uid_value)
        return super(EEAReferenceField, self).set(instance, value, **kwargs)

    def getRaw(self, instance, aslist=False, **kwargs):
        """ If exists, use the values from eea_refs attribute
        """
        res = super(EEAReferenceField, self).getRaw(instance, aslist, **kwargs)
        if not hasattr(instance, "eea_refs"):
            return res

        return [r for r in instance.eea_refs]
