# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as publishged by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref test for OAI-PMH export"""

from collections import namedtuple
from functools import wraps
import time

from dateutil.parser import parse as parse_date
from lxml import etree
import pytz

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.pyramid.test import PyramidCWTest

from cubes.oaipmh.views import OAIError, OAIRequest

from cubicweb_saem_ref import permanent_url

import testutils

EntityInfo = namedtuple('EntityInfo', ['ark', 'url', 'eid'])


def publish_entity(entity):
    """Fire "publish" transition for `entity`."""
    entity.cw_adapt_to('IWorkflowable').fire_transition('publish')
    entity._cw.commit()


def deprecate_entity(entity):
    """Fire "deprecate" transition for `entity`."""
    entity.cw_adapt_to('IWorkflowable').fire_transition('deprecate')
    entity._cw.commit()


class OAITestMixin(object):

    def oai_component(self, cnx):
        """Return the "oai" component"""
        return self.vreg['components'].select('oai', cnx)


class OAIComponentTC(CubicWebTC, OAITestMixin):

    def test_registered(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            setspecs = oai.__setspecs__
            self.assertCountEqual(setspecs.keys(),
                                  ['agent', 'organizationunit', 'organization',
                                   'authorityrecord',
                                   'conceptscheme', 'profile', 'concept'])
            self.assertCountEqual(setspecs['organizationunit'].keys(), ['role'])
            self.assertCountEqual(setspecs['profile'].keys(),
                                  ['transferring_agent'])
            self.assertEqual(setspecs['conceptscheme'].keys(), [])
            self.assertEqual(setspecs['authorityrecord'].keys(), ['used_by'])

    def test_setspecs(self):
        with self.admin_access.repo_cnx() as cnx:
            arch = testutils.organization_unit(
                cnx, u'arch', archival_roles=[u'archival'])
            ark = testutils.organization_unit(
                cnx, u'dep', archival_roles=[u'deposit']).ark
            scheme = testutils.setup_scheme(cnx, u'test', u'lab')
            cnx.commit()
            publish_entity(scheme)
            expected = (
                'agent',
                'authorityrecord',
                'authorityrecord:used_by:%s' % arch.ark,
                'authorityrecord:used_by:%s' % ark,
                'organization',
                'organizationunit',
                'organizationunit:role:producer',
                'organizationunit:role:deposit',
                'organizationunit:role:archival',
                'organizationunit:role:control',
                'organizationunit:role:enquirer',
                'organizationunit:role:seda-actor',
                'conceptscheme',
                'profile', 'profile:transferring_agent:%s' % ark,
                'concept', 'concept:in_scheme:%s' % scheme.ark
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)


def setup_organization_units(cnx):
    """Create two agents (alice and bobby) in published state and return their
    (ark, url, eid) attributes.
    """
    alice = testutils.organization_unit(cnx, u'alice',
                                        archival_roles=[u'producer'])
    cnx.commit()
    bobby = testutils.organization_unit(cnx, u'bobby',
                                        archival_roles=[u'enquirer'])
    cnx.commit()

    return (
        EntityInfo(alice.ark, permanent_url(alice), alice.eid),
        EntityInfo(bobby.ark, permanent_url(bobby), bobby.eid),
    )


class OAIRequestTC(CubicWebTC):

    def test_rset(self):
        """Test `rset` function for exceptions."""
        with self.admin_access.repo_cnx() as cnx:
            return setup_organization_units(cnx)
        with self.admin_access.web_request() as req:
            for setspec, msg in [
                ('organizationunit:zen', 'invalid set specifier organizationunit:zen'),
                ('organizationunit:role:control', (
                    'The combination of the values of the from, until, and '
                    'set arguments results in an empty list.')),
                ('conceptscheme:haha', 'invalid set specifier conceptscheme:haha'),
                ('scregneugneu', 'invalid set specifier scregneugneu'),
            ]:
                with self.subTest(setspec=setspec):
                    oairq = OAIRequest('https://localhost:80', setspec=setspec)
                    with self.assertRaises(OAIError) as cm:
                        oairq.rset_from_setspec(req)
                    self.assertEqual(cm.exception.errors, {'noRecordsMatch': msg})


def no_validate_xml(method):
    """Disable XML schema validation, often because the underlying metadata
    part of the response (RDF, XSD) is not validable (or we don't know how to
    do it).
    """
    @wraps(method)
    def wrapper(self):
        self._validate_xml = False
        self._debug_xml = True
        return method(self)
    return wrapper


class OAIPMHViewsTC(PyramidCWTest, OAITestMixin, testutils.XmlTestMixin):
    settings = {
        # to get clean traceback in tests (instead of in an html error page)
        'cubicweb.bwcompat': False,
        # avoid noise in test output (UserWarning: !! WARNING WARNING !! you
        # should stop this instance)
        'cubicweb.session.secret': 'x',
        'cubicweb.auth.authtkt.session.secret': 'x',
        'cubicweb.auth.authtkt.persistent.secret': 'x',
    }

    _validate_xml = True
    _debug_xml = False

    def oai_request(self, req, **formparams):
        response = self.webapp.get('/oai', formparams)
        self.assertEqual(response.headers['Content-Type'], 'text/xml; charset=UTF-8')
        if self._validate_xml:
            self.assertXmlValid(response.body, self.datapath('OAI-PMH.xsd'),
                                debug=self._debug_xml)
        return response.body

    def _setup_organization_units(self, **kwargs):
        with self.admin_access.repo_cnx() as cnx:
            return setup_organization_units(cnx, **kwargs)

    def test_xml_attributes_and_namespaces(self):
        """Check XML attributes and namespace declaration of the response."""
        with self.admin_access.web_request() as req:
            # simple request, generating an error but enough to get a properly
            # formatter response.
            result = self.oai_request(req)
            xml = etree.fromstring(result)
            nsmap = {None: 'http://www.openarchives.org/OAI/2.0/',
                     'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
            self.assertEqual(xml.nsmap, nsmap)
            attrib = {
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': ' '.join(
                    ['http://www.openarchives.org/OAI/2.0/',
                     'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd']),
            }
            self.assertEqual(xml.attrib, attrib)

    def _setup_schemes(self):
        with self.admin_access.repo_cnx() as cnx:
            pscheme = testutils.setup_scheme(cnx, u'public',
                                             u'public label', u'other public label')
            # draft ConceptScheme
            dscheme = testutils.setup_scheme(cnx, u'draft',
                                             u'draft label', u'other draft label')
            cnx.commit()
            publish_entity(pscheme)
            return (
                EntityInfo(pscheme.ark, pscheme.absolute_url(), pscheme.eid),
                EntityInfo(dscheme.ark, dscheme.absolute_url(), dscheme.eid),
            )

    def test_noverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req)
        self.assertIn('<request>https://localhost:80/oai</request>',
                      result)
        self.assertIn('<error code="badVerb">no verb specified</error',
                      result)

    def test_badverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='coucou')
        self.assertIn('<request>https://localhost:80/oai</request>',
                      result)
        self.assertIn('<error code="badVerb">illegal verb "coucou"</error>',
                      result)

    # some of our setspecs (those with an ARK inside are not valid)
    @no_validate_xml
    def test_listsets(self):
        pscheme, dscheme = self._setup_schemes()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListSets')
        self.assertIn('<request verb="ListSets">https://localhost:80/oai</request>',
                      result)
        for spec in ('agent', 'organizationunit', 'conceptscheme', 'profile',
                     'concept'):
            self.assertIn('<setSpec>{0}</setSpec>'.format(spec),
                          result)
        self.assertIn(('<setSpec>organizationunit:role:deposit</setSpec>'
                       '<setName>An organization unit with deposit archival role</setName>'),
                      result)
        self.assertIn('<setSpec>concept:in_scheme:{0}</setSpec>'.format(pscheme.ark),
                      result)
        self.assertNotIn(dscheme.ark, result)

    def _setup_profile(self, **kwargs):
        """Create a "published" SEDAArchiveTransfer and return it."""
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_profile(cnx, **kwargs)
            cnx.commit()
            publish_entity(profile)
            profile.ark  # prefetch attribute for later usage
            return profile

    def test_listidentifiers(self):
        alice, bobby = [x.ark for x in self._setup_organization_units()]
        profile = self._setup_profile()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='organizationunit',
                                      metadataPrefix='rdf')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(bobby), result)
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(alice), result)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='organizationunit:role:producer',
                                      metadataPrefix='rdf')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(alice),
                          result)
            self.assertNotIn('<identifier>ark:/{0}</identifier>'.format(bobby),
                             result)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='organizationunit:role:producer',
                                      metadataPrefix='rdf')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(alice), result)
            self.assertNotIn('<identifier>ark:/{0}</identifier>'.format(bobby), result)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='conceptscheme',
                                      metadataPrefix='rdf')
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='profile', metadataPrefix='seda02xsd')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile.ark), result)

    def test_listidentifiers_deleted(self):
        """Check <header> element (status attribute, datestamp) for deleted
        records in ListIdentifiers response.
        """
        alice, bobby = self._setup_organization_units()
        with self.admin_access.repo_cnx() as cnx:
            entity = cnx.entity_from_eid(bobby.eid)
            # ensure transition date is greater by at least 1s
            time.sleep(1)
            date_before = entity.modification_date.replace(tzinfo=pytz.utc)
            deprecate_entity(entity)

        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='organizationunit',
                                      metadataPrefix='rdf')
            self.assertIn(
                '<identifier>ark:/{0}</identifier>'.format(bobby.ark), result)
            self.assertIn('<header status="deleted">', result)
            root = etree.fromstring(result)
            ns = root.nsmap[None]
            # only one <header status="..."> element
            header, = root.findall('.//{%s}header[@status]' % ns)
            datestamp = header.find('{%s}datestamp' % ns).text
            date = parse_date(datestamp)
            self.assertGreater(date, date_before.replace(microsecond=0))

    @no_validate_xml
    def test_listrecords(self):
        alice, bobby = self._setup_organization_units()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='organizationunit',
                                      metadataPrefix='rdf')
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(bobby.url), result)
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(alice.url), result)
            result = self.oai_request(
                req, verb='ListRecords', set='organizationunit:role:producer',
                metadataPrefix='rdf')
            self.assertIn(
                '<rdf:Description rdf:about="{0}">'.format(alice.url), result)
            self.assertNotIn(bobby.url, result)

    @no_validate_xml
    def test_listrecords_profile(self):
        self._setup_profile()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='profile',
                                      metadataPrefix='seda02xsd')
        # Just ensure a SEDA profile (xsd) is present in response.
        self.assertIn('<metadata><xsd:schema', result)
        self.assertIn('fr:gouv:ae:archive:draft:standard_echange_v0.2', result)

    @no_validate_xml
    def test_listidentifiers_profile_setspec(self):
        """Check setspec restriction for SEDAArchiveTransfer."""
        profile = self._setup_profile()
        with self.admin_access.cnx() as cnx:
            tagent_eid = testutils.organization_unit(
                cnx, u'blah', archival_roles=[u'deposit']).eid
            cnx.commit()
        profile2 = self._setup_profile()
        with self.admin_access.cnx() as cnx:
            cnx.entity_from_eid(tagent_eid).cw_set(use_profile=profile2.eid)
            cnx.commit()
        with self.admin_access.web_request() as req:
            transferring_agent_ark = req.entity_from_eid(tagent_eid).ark
            result = self.oai_request(
                req, verb='ListIdentifiers',
                set='profile:transferring_agent:' + transferring_agent_ark,
                metadataPrefix='seda02xsd')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile2.ark), result)
            self.assertNotIn(profile.ark, result)
        # Check that without a setspec, we get all profiles.
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='profile', metadataPrefix='seda02xsd')
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile.ark), result)
            self.assertIn('<identifier>ark:/{0}</identifier>'.format(profile2.ark), result)

    @no_validate_xml
    def test_getrecord_profile(self):
        profile = self._setup_profile()
        with self.admin_access.web_request() as req:
            with self.subTest(md_prefix='seda02xsd'):
                result = self.oai_request(req, verb='GetRecord',
                                          identifier='ark:/' + profile.ark,
                                          metadataPrefix='seda02xsd')
                self.assertIn('<metadata><xsd:schema', result)
                self.assertIn('http://www.w3.org/2001/XMLSchema', result)
            for md_prefix in ['seda02rng', 'seda1rng', 'seda2rng']:
                with self.subTest(md_prefix=md_prefix):
                    result = self.oai_request(req, verb='GetRecord',
                                              identifier='ark:/' + profile.ark,
                                              metadataPrefix=md_prefix)
                    self.assertIn('<metadata><rng:grammar', result)
                    self.assertIn('http://www.w3.org/2001/XMLSchema', result)

    @no_validate_xml
    def test_getrecord_agent(self):
        self._debug_xml = True
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.agent(cnx, u'toto')
            cnx.commit()
            ark = agent.ark
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier='ark:/' + ark,
                                      metadataPrefix='rdf')
            self.assertIn('name>toto</', result)
            self.assertIn('<rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>',
                          result)

    @no_validate_xml
    def test_getrecord_organization(self):
        with self.admin_access.repo_cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            cnx.commit()
            ark = org.ark
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier='ark:/' + ark,
                                      metadataPrefix='rdf')
            self.assertIn('title>Default authority</', result)
            self.assertIn('<rdf:type rdf:resource="http://www.w3.org/ns/org#Organization"/>',
                          result)

    @no_validate_xml
    def test_getrecord_organizationunit(self):
        self._debug_xml = True
        with self.admin_access.repo_cnx() as cnx:
            orgu = testutils.organization_unit(cnx, u'toto')
            cnx.commit()
            ark = orgu.ark
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier='ark:/' + ark,
                                      metadataPrefix='rdf')
            self.assertIn('title>toto</', result)
            self.assertIn('<rdf:type rdf:resource="http://www.w3.org/ns/org#OrganizationUnit"/>',
                          result)

    @no_validate_xml
    def test_getrecord_authority_record(self):
        with self.admin_access.repo_cnx() as cnx:
            arecord = testutils.authority_record(cnx, u'M. Person')
            cnx.commit()
            arecord.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            arecord_ark = arecord.ark
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier='ark:/' + arecord_ark,
                                      metadataPrefix='eac')
            self.assertIn('<metadata><eac-cpf', result)
            self.assertIn('urn:isbn:1-931666-33-4', result)

    @no_validate_xml
    def test_authorityrecord_from_organizationunit(self):
        with self.admin_access.cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            ou_ark = testutils.organization_unit(
                cnx, u'test', archival_roles=('archival', ),
                reverse_archival_unit=org, authority=org).ark
            self.create_user(cnx, u'bob', authority=org)
            cnx.commit()
        with self.new_access(u'bob').cnx() as cnx:
            arecord = testutils.authority_record(cnx, u'test')
            cnx.commit()
            assert arecord.reverse_use_authorityrecord
            arecord.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            ark = arecord.ark
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb='ListIdentifiers',
                set='authorityrecord:used_by:{}'.format(ou_ark),
                metadataPrefix='eac')
            self.assertIn('<identifier>ark:/' + ark, result)


if __name__ == '__main__':
    import unittest
    unittest.main()
