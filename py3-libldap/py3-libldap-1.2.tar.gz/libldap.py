#!/usr/bin/env python3

from _libldap import *

class LDAP(LDAP_):
    def __init__(self, uri, version=LDAP_VERSION3):
        super(LDAP, self).__init__(uri, version)

    def get_schema(self):
        keys2parse = {
            'ldapSyntaxes': ldap_str2syntax,
            'matchingRules': ldap_str2matchingrule,
            'matchingRuleUse': ldap_str2matchingruleuse,
            'attributeTypes': ldap_str2attributetype,
            'objectClasses': ldap_str2objectclass
            }
        raw = self.search_ext_s(
            LDAP_SCHEMA_BASE, scope=LDAP_SCOPE_BASE, attrs=['+'])
        ret = []
        for r in raw:
            d = {}
            for key in r[1]:
                if key in keys2parse:
                    d[key] = [keys2parse[key](v) for v in r[1][key]]
                else:
                    d[key] = r[1][key]
            ret.append((r[0], d))
        return ret

class LDAPMods(list):
    def __init__(self, mode, **attrs):
        if mode not in (LDAP_MOD_ADD, LDAP_MOD_DELETE, LDAP_MOD_REPLACE):
            raise TypeError(
                "%s.__init__(): argument `mode' " % self.__class__.__name__ +
                'must be LDAP_MOD_[ADD|DELETE|REPLACE]'
                )
        super(LDAPMods, self).__init__()
        for attr in attrs:
            try:
                if mode == LDAP_MOD_DELETE:
                    lm = LDAPMod(mode, attr)
                else:
                    lm = LDAPMod(mode, attr, attrs[attr])
            except Exception as msg:
                raise LDAPError(
                    "%s.__init__(): `%s': %s" %
                    (self.__class__.__name__, attr, msg)
                    ) from None
            self.append(LDAPMod(mode, attr, attrs[attr]))
