from cubicweb_saem_ref.hooks import set_ark_and_cwuri


def fix_organization_ark(cnx):
    with cnx.security_enabled(write=False):
        rset = cnx.execute('Any O WHERE O ark NULL, O is Organization')
        for org in rset.entities():
            if org.ark_naa:
                naa_what = org.ark_naa[0].what
            else:
                # set dumb naa what that will have to be fixed later by hand,
                # but at least it will appear in the UI
                naa_what = u'XXX'
            attrs = {}
            set_ark_and_cwuri(cnx, org.eid, 'Organization', attrs, naa_what=naa_what)
            org.cw_set(**attrs)
        cnx.commit()


fix_organization_ark(cnx)
