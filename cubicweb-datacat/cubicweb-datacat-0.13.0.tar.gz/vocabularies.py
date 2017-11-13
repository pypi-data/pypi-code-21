# -*- coding: utf-8 -*-
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
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
"""cubicweb-datacat vocabularies (concept schemes)"""

from os.path import (
    dirname,
    join,
)
import re

from cubicweb.dataimport import (
    massive_store,
    stores,
    ucsvreader,
)
from cubicweb.dataimport.importer import (
    ExtEntity,
    SimpleImportLog,
)

from cubes.skos import rdfio
from cubes.skos.sobjects import import_skos_extentities


DCAT_SCHEMES = [
    (u'ADMS vocabularies',
     u'https://joinup.ec.europa.eu/svn/adms/ADMS_v1.00/ADMS_SKOS_v1.00.rdf'),
    (u'European Frequency Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/frequency/skos/frequencies-skos.rdf'),
    (u'European Filetypes Authority Table',
     u'http://publications.europa.eu/mdr/resource/authority/file-type/skos/filetypes-skos.rdf'),
    (u'European Languages Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/language/skos/languages-skos.rdf'),
    (u'European Dataset Theme Vocabulary',
     u'http://publications.europa.eu/mdr/resource/authority/data-theme/skos/data-theme-skos.rdf'),
    (u'European Licences Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/licence/skos/licences-skos.rdf'),
    (u'European Country Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/country/skos/countries-skos.rdf'),
    (u'European Places Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/place/skos/places-skos.rdf'),
    (u'European Continents Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/continent/skos/continents-skos.rdf'),
]

EUROVOC_URI = (u'http://publications.europa.eu/mdr/resource/thesaurus/eurovoc-20150416-0/skos/'
               'eurovoc_skos.zip')

LICENSE_SCHEME = u'http://publications.europa.eu/resource/authority/licence'

ADMS_FRENCH_LABELS = {
    'http://purl.org/adms/assettype/CodeList': u'Liste de codes',
    'http://purl.org/adms/assettype/CoreComponent': u'Composant commun',
    'http://purl.org/adms/assettype/DomainModel': u'Modèle de domaine',
    # 'http://purl.org/adms/assettype/InformationExchangePackageDescription': u'',
    'http://purl.org/adms/assettype/Mapping': u'Correspondance',
    'http://purl.org/adms/assettype/NameAuthorityList': u"Liste de noms d'autorité",
    'http://purl.org/adms/assettype/Ontology': u'Ontologie',
    'http://purl.org/adms/assettype/Schema': u'Schéma',
    'http://purl.org/adms/assettype/ServiceDescription': u"Description d'un service",
    'http://purl.org/adms/assettype/SyntaxEncodingScheme': u"Système d'encodage",
    'http://purl.org/adms/assettype/Taxonomy': u'Taxonomie',
    'http://purl.org/adms/assettype/Thesaurus': u'Thésaurus',
    'http://purl.org/adms/interoperabilitylevel/Legal': u'Légal',
    'http://purl.org/adms/interoperabilitylevel/Organisational': u'Organisationnel',
    'http://purl.org/adms/interoperabilitylevel/Political': u'Politique',
    'http://purl.org/adms/interoperabilitylevel/Semantic': u'Sémantique',
    'http://purl.org/adms/interoperabilitylevel/Technical': u'Technique',
    'http://purl.org/adms/licencetype/Attribution': u'Attribution',
    # 'http://purl.org/adms/licencetype/GrantBack': u'',
    'http://purl.org/adms/licencetype/JurisdictionWithinTheEU': (
        u"Compétence d'une juridiction de l'UE"
    ),
    'http://purl.org/adms/licencetype/KnownPatentEncumbrance': u'Protégé par brevet',
    'http://purl.org/adms/licencetype/NoDerivativeWork': u'Pas de modification',
    'http://purl.org/adms/licencetype/NominalCost': u'Contribution nominale',
    'http://purl.org/adms/licencetype/NonCommercialUseOnly': u"Pas d'utilisation commerciale",
    'http://purl.org/adms/licencetype/OtherRestrictiveClauses': u'Autres clauses restrictives',
    'http://purl.org/adms/licencetype/PublicDomain': u'Domaine public',
    'http://purl.org/adms/licencetype/ReservedNames-Endorsement-OfficialStatus': (
        u'Utilisation du nom ou de la marque interdite'
    ),
    'http://purl.org/adms/licencetype/RoyaltiesRequired': u'Soumis à redevance',
    'http://purl.org/adms/licencetype/UnknownIPR': u'Inconnu',
    'http://purl.org/adms/licencetype/ViralEffect-ShareAlike': u'Partage dans les mêmes conditions',
    'http://purl.org/adms/publishertype/Academia-ScientificOrganisation': (
        u'Académique/Organisation scientifique'
    ),
    'http://purl.org/adms/publishertype/Company': u'Société',
    'http://purl.org/adms/publishertype/IndustryConsortium': u'Consortium industriel',
    'http://purl.org/adms/publishertype/LocalAuthority': u'Collectivité locale',
    'http://purl.org/adms/publishertype/NationalAuthority': u'Administration nationale',
    'http://purl.org/adms/publishertype/NonGovernmentalOrganisation': (
        u'Organisation non gouvernementale'
    ),
    'http://purl.org/adms/publishertype/NonProfitOrganisation': u'Organisation à but non lucratif',
    'http://purl.org/adms/publishertype/PrivateIndividual(s)': u'Individu(s)',
    'http://purl.org/adms/publishertype/RegionalAuthority': u'Autorité régionale',
    'http://purl.org/adms/publishertype/StandardisationBody': u'Organisme de standardisation',
    'http://purl.org/adms/publishertype/SupraNationalAuthority': u'Autorité supra-nationale',
    'http://purl.org/adms/representationtechnique/Archimate': u'Archimate',
    'http://purl.org/adms/representationtechnique/BPMN': u'BPMN',
    'http://purl.org/adms/representationtechnique/CommonLogic': u'Common logic',
    'http://purl.org/adms/representationtechnique/DTD': u'DTD',
    'http://purl.org/adms/representationtechnique/Datalog': u'Datalog',
    'http://purl.org/adms/representationtechnique/Diagram': u'Diagramme',
    'http://purl.org/adms/representationtechnique/Genericode': u'genericode',
    'http://purl.org/adms/representationtechnique/HumanLanguage': u'Langue naturelle',
    'http://purl.org/adms/representationtechnique/IDEF': u'IDEF',
    'http://purl.org/adms/representationtechnique/KIF': u'KIF',
    'http://purl.org/adms/representationtechnique/OWL': u'OWL',
    'http://purl.org/adms/representationtechnique/Prolog': u'Prolog',
    'http://purl.org/adms/representationtechnique/RDFSchema': u'RDFS',
    'http://purl.org/adms/representationtechnique/RIF': u'RIF',
    'http://purl.org/adms/representationtechnique/RelaxNG': u'Relax NG',
    'http://purl.org/adms/representationtechnique/RuleML': u'RuleML',
    'http://purl.org/adms/representationtechnique/SBVR': u'SBVR',
    'http://purl.org/adms/representationtechnique/SKOS': u'SKOS',
    'http://purl.org/adms/representationtechnique/SPARQL': u'SPARQL',
    'http://purl.org/adms/representationtechnique/SPIN': u'SPIN',
    'http://purl.org/adms/representationtechnique/SWRL': u'SWRL',
    'http://purl.org/adms/representationtechnique/Schematron': u'Schematron',
    'http://purl.org/adms/representationtechnique/TopicMaps': u'Carte thématique',
    'http://purl.org/adms/representationtechnique/UML': u'UML',
    'http://purl.org/adms/representationtechnique/WSDL': u'WSDL',
    'http://purl.org/adms/representationtechnique/WSMO': u'WSMO',
    'http://purl.org/adms/representationtechnique/XMLSchema': u'XSD',
    'http://purl.org/adms/status/Completed': u'Terminé',
    'http://purl.org/adms/status/Deprecated': u'Deprécié',
    'http://purl.org/adms/status/UnderDevelopment': u'En développement',
    'http://purl.org/adms/status/Withdrawn': u'Abandonné',
}


def add_source(cnx, name, url):
    return cnx.create_entity('SKOSSource', name=name, url=url)


def datapath(fname):
    return join(dirname(__file__), 'migration', 'data', fname)


def media_types_extentities(media_types=None):
    """Yield ExtEntity objects fetch from parsing IANA CSV files from
    http://www.iana.org/assignments/media-types/media-types.xml.

    If media_types is specified, it should be a list of domain to import.
    Otherwise all domains will be imported.
    """
    iana_uri = 'http://www.iana.org/assignments/media-types/media-types.xml'
    yield ExtEntity('ConceptScheme', iana_uri, {'title': set([u'IANA Media Types'])})
    if media_types is None:
        media_types = ('application', 'audio', 'image', 'message', 'model',
                       'multipart', 'text', 'video')
    for typename in media_types:
        with open(datapath(typename + '.csv')) as f:
            reader = ucsvreader(f, encoding='utf-8', delimiter=',', skipfirst=True)
            concepts = set([])
            for line in reader:
                fulltypename = typename + '/' + line[0]
                if fulltypename in concepts:
                    # Only consider first occurences.
                    continue
                concepts.add(fulltypename)
                yield ExtEntity('Concept', fulltypename, {'in_scheme': set([iana_uri])})
                yield ExtEntity('Label', fulltypename + '_label',
                                {'label': set([fulltypename]),
                                 'language_code': set([u'en']),
                                 'kind': set([u'preferred']),
                                 'label_of': set([fulltypename])})


def media_types_import(cnx, **kwargs):
    """Import of IANA media types concepts from CSV files."""
    import_log = SimpleImportLog('Media Types')
    if cnx.repo.system_source.dbdriver == 'postgres':
        store = massive_store.MassiveObjectStore(cnx)
    else:
        store = stores.NoHookRQLObjectStore(cnx)
    stats, (scheme, ) = import_skos_extentities(
        cnx, media_types_extentities(**kwargs), import_log, store=store,
        raise_on_error=True)
    return stats, scheme


def capitalized_eurovoc_domain(domain):
    """Return the given Eurovoc domain name with only the first letter uppercase."""
    return re.sub(r'^(\d+\s)(.+)$',
                  lambda m: u'{0}{1}'.format(m.group(1), m.group(2).lower().capitalize()),
                  domain, re.UNICODE)


def simplify_eurovoc(eurovoc_graph, new_graph):  # noqa (mccabe too complex)
    """Simplify the original Eurovoc thesaurus so that it can be used in cubicweb-skos.

    First given graph (``eurovoc_graph``) is an rdfio graph containing original Eurovoc thesaurus
    in RDF. Then, second graph (``new_graph``) will be populated with simplified triples.

    Actual simplifications are done like the this:

    * each of the 21 Eurovoc domain is used as a concept scheme with a ``dcterms:title`` property
    * each of the 127 Eurovoc micro thesaurus is used as a concept (it thus becomes a top concept
      of the corresponding domain),
    * for each micro thesaurus (which becomes a concept), its former top concepts become narrower
      concepts,
    * for each micro thesaurus, all of its concepts become concepts of the coresponding domain
      concept scheme (that is ``skos:inScheme`` property object become the domain).

    """
    reg = rdfio.RDFRegistry()
    uri = reg.normalize_uri
    uriobject = eurovoc_graph.uri
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('dcterms', 'http://purl.org/dc/terms/')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_prefix('skos-xl', 'http://www.w3.org/2008/05/skos-xl#')
    reg.register_prefix('eu', 'http://eurovoc.europa.eu/schema#')
    reg.register_prefix('thes', 'http://purl.org/iso25964/skos-thes#')
    eurovoc_uri = u'http://eurovoc.europa.eu/100141'
    microthes2domain = dict((mt_uri, next(eurovoc_graph.objects(mt_uri, uri('eu:domain'))))
                            for mt_uri in eurovoc_graph.uris_for_type(uri('eu:MicroThesaurus')))
    for subj_uri, pred_uri, obj_uri in eurovoc_graph.triples():
        is_active = (u'http://publications.europa.eu/resource/authority/status/deprecated' not in
                     list(eurovoc_graph.objects(subj_uri, uri('thes:status'))))
        # Convert eu:Domain into a skos:ConceptScheme
        if obj_uri == uri('eu:Domain'):
            new_graph.add(uriobject(subj_uri), uriobject(uri('rdf:type')),
                          uriobject(uri('skos:ConceptScheme')))
            for title in eurovoc_graph.objects(subj_uri, uri('skos:prefLabel')):
                if title.lang == u'fr':
                    new_graph.add(uriobject(subj_uri), uriobject(uri('dcterms:title')),
                                  capitalized_eurovoc_domain(title))
                    break
        # Convert eu:MicroThesaurus into a skos:Concept
        elif obj_uri == uri('eu:MicroThesaurus'):
            new_graph.add(uriobject(subj_uri), uriobject(uri('rdf:type')),
                          uriobject(uri('skos:Concept')))
            scheme_uri = next(eurovoc_graph.objects(subj_uri, uri('eu:domain')))
            new_graph.add(uriobject(subj_uri), uriobject(uri('skos:inScheme')),
                          uriobject(scheme_uri))
        # Convert eu:ThesaurusConcept into a skos:Concept if not deprecated
        elif obj_uri == uri('eu:ThesaurusConcept'):
            new_graph.add(uriobject(subj_uri), uriobject(uri('rdf:type')),
                          uriobject(uri('skos:Concept')))
        # Replace <concept> topConceptOf <MicroThesaurus> by <concept> broader <MicroThesaurus>
        elif is_active and pred_uri == uri('skos:topConceptOf'):
            new_graph.add(uriobject(subj_uri), uriobject(uri('skos:broader')), uriobject(obj_uri))
        # Replace <concept> skos:inScheme <MicroThes> by <concept> skos:broader <MicroThes>
        # and <concept> skos:inScheme <Domain>
        elif is_active and pred_uri == uri('skos:inScheme') and obj_uri in microthes2domain:
            new_graph.add(uriobject(subj_uri), uriobject(uri('skos:inScheme')),
                          uriobject(microthes2domain[obj_uri]))
        # Keep label triples
        elif (is_active and obj_uri != eurovoc_uri and subj_uri != eurovoc_uri and
              pred_uri in (uri('skos:prefLabel'), uri('skos:altLabel'), uri('skos:hiddenLabel'))):
            new_graph.add(uriobject(subj_uri), uriobject(pred_uri), obj_uri)
        # Keep existing skos:broader relations
        elif is_active and pred_uri == uri('skos:broader'):
            new_graph.add(uriobject(subj_uri), uriobject(pred_uri), uriobject(obj_uri))
        # Keep existing concepts
        elif is_active and obj_uri == uri('skos:Concept'):
            new_graph.add(uriobject(subj_uri), uriobject(pred_uri), uriobject(obj_uri))


def eurovoc_domains(simplified_graph):
    """Return a dictionary containing all Eurovoc domains with their URIs.

    Keys are domain URIs and values are domain titles (in french).
    """
    reg = rdfio.RDFRegistry()
    uri = reg.normalize_uri
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_prefix('dcterms', 'http://purl.org/dc/terms/')
    domains = {}
    for domain_uri in simplified_graph.uris_for_type(uri('skos:ConceptScheme')):
        domains[domain_uri] = unicode(next(simplified_graph.objects(domain_uri,
                                                                    uri('dcterms:title'))))
    return domains
