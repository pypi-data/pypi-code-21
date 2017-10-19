# coding: utf-8
# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref site customizations"""

import pytz

from logilab.common.date import ustrftime
from logilab.common.decorators import monkeypatch

from cubicweb import cwvreg, _
from cubicweb.cwconfig import register_persistent_options
from cubicweb.uilib import PRINTERS
from cubicweb.entity import Entity
from cubicweb.web import request

from cubes.skos import rdfio
from cubes.skos.ccplugin import ImportSkosData
import cubicweb_seda as seda
import cubicweb_seda.dataimport as seda_dataimport

from . import permanent_url, _massive_store_factory, _nohook_store_factory

# this import is needed to take account of pg_trgm monkeypatches
# while executing cubicweb-ctl commands (db-rebuild-fti)
from . import pg_trgm  # noqa pylint: disable=unused-import


# override Entity.rest_path to use ark for entities which have one

_orig_rest_path = Entity.rest_path


@monkeypatch(Entity)
def rest_path(self, *args, **kwargs):
    """Return ark:/<ARK> is entity has an ark attribute."""
    if getattr(self, 'ark', None) is None:
        return _orig_rest_path(self, *args, **kwargs)
    return u'ark:/' + self.ark


# configure RDF generator to use ark based uri as canonical uris, and deactivating implicit
# 'same_as_urls' in this case

orig_same_as_uris = rdfio.RDFGraphGenerator.same_as_uris


@monkeypatch(rdfio.RDFGraphGenerator, methodname='same_as_uris')
@staticmethod
def same_as_uris(entity):
    if entity.cwuri.startswith('ark:'):
        return ()
    return orig_same_as_uris(entity)


@monkeypatch(rdfio.RDFGraphGenerator, methodname='canonical_uri')
@staticmethod
def canonical_uri(entity):
    return permanent_url(entity)


# deactivate date-format and datetime-format cw properties. This is because we do some advanced date
# manipulation such as allowing partial date and this is not generic enough to allow arbitrary
# setting of date and time formats

base_user_property_keys = cwvreg.CWRegistryStore.user_property_keys


@monkeypatch(cwvreg.CWRegistryStore)
def user_property_keys(self, withsitewide=False):
    props = base_user_property_keys(self, withsitewide)
    return [prop for prop in props if prop not in ('ui.date-format', 'ui.datetime-format')]


# customize display of TZDatetime

register_persistent_options((
    ('timezone',
     {'type': 'choice',
      'choices': pytz.common_timezones,
      'default': 'Europe/Paris',
      'help': _('timezone in which time should be displayed'),
      'group': 'ui', 'sitewide': True,
      }),
))


def print_tzdatetime_local(value, req, *args, **kwargs):
    tz = pytz.timezone(req.property_value('ui.timezone'))
    value = value.replace(tzinfo=pytz.utc).astimezone(tz)
    return ustrftime(value, req.property_value('ui.datetime-format'))


PRINTERS['TZDatetime'] = print_tzdatetime_local


# configure c-c skos-import command's factories to use with proper metadata generator ##############

ImportSkosData.cw_store_factories['massive'] = _massive_store_factory
ImportSkosData.cw_store_factories['nohook'] = _nohook_store_factory


# override seda's scheme initialization to set ark on each scheme, and to use an ark enabled store

@monkeypatch(seda_dataimport)
def init_seda_scheme(cnx, title, _count=[]):
    description = u'edition 2009' if title.startswith('SEDA :') else None
    # 25651 = Archives départementales de la Gironde (ADGIRONDE)
    # XXX ensure that:
    # * NAA for those vocabulary is 25651
    # * generated ark are identical from one instance to another (for scheme and concepts, see
    #   below)

    if not _count:
        rset = cnx.execute(
            'String ARK ORDERBY CD DESC LIMIT 1'
            ' WHERE X creation_date CD, X ark LIKE "25651/v%", X ark ARK'
        )
        if not rset:
            value = 0
        else:
            value = int(rset[0][0][len('25651/v'):])
        _count.append(value)

    _count[0] += 1
    ark = u'25651/v%s' % _count[0]
    if cnx.vreg.config.repairing:  # XXX seda 0.8 migration
        ark_hack = {
            u'SEDA 2 : Status légaux': 20,
            u'SEDA : Règles de diffusion': 21,
            u"Algorithmes d'empreinte": 22,
        }
        try:
            ark = u'25651/v%s' % ark_hack[title]
        except KeyError:
            pass
    scheme = cnx.create_entity('ConceptScheme', title=title, description=description, ark=ark)
    seda_dataimport.EXTID2EID_CACHE['ark:/' + ark] = scheme.eid
    return scheme


@monkeypatch(seda_dataimport)
def get_store(cnx):
    from .sobjects import SAEMMetadataGenerator
    metagen = SAEMMetadataGenerator(cnx, naa_what='25651')
    if cnx.repo.system_source.dbdriver == 'postgres':
        from cubicweb.dataimport.massive_store import MassiveObjectStore
        return MassiveObjectStore(cnx, metagen=metagen, eids_seq_range=1000)
    else:
        from cubicweb.dataimport.stores import NoHookRQLObjectStore
        return NoHookRQLObjectStore(cnx, metagen=metagen)


# configure seda compound graph to discard Activity and its relations, else it
# causes problem because it belongs to several graphs with different compound
# implementation (using "container" relation or not)
seda.GRAPH_SKIP_ETYPES.add('Activity')
# also, the new_version_of relation should not be considered as part of the
# graph (as for e.g. container or clone_of)
for rtype in ('new_version_of', 'use_profile'):
    seda.GRAPH_SKIP_RTYPES.add(rtype)
    Entity.cw_skip_copy_for.append((rtype, 'subject'))
    Entity.cw_skip_copy_for.append((rtype, 'object'))


@monkeypatch(request._CubicWebRequestBase)
def negotiated_language(self):
    # Force language to fr since in http-negociation mode there is no way to
    # force french language with a browser configured in english.
    # This is currently the easiest way to force the language of an instance.
    return 'fr'


####################################################################################################
# temporary monkey-patches #########################################################################
####################################################################################################

# avoid disappearance of navtop components (https://www.cubicweb.org/17074195)
# other part lies in views/patches.py

from cubicweb.utils import json_dumps, js_href  # noqa
from cubicweb.web import component  # noqa


@monkeypatch(component.NavigationComponent)
def ajax_page_url(self, **params):
    divid = params.setdefault('divid', 'contentmain')
    params['rql'] = self.cw_rset.printable_rql()
    return js_href("$(%s).loadxhtml(AJAX_PREFIX_URL, %s, 'get', 'swap')" % (
        json_dumps('#' + divid), component.js.ajaxFuncArgs('view', params)))


# Fixed rql reqwrite (https://www.cubicweb.org/ticket/17074119)

from cubicweb.rqlrewrite import RQLRewriter, n, remove_solutions  # noqa


def need_exists(node):
    """Return true if the given node should be wrapped in an `Exists` node.

    This is true when node isn't already an `Exists` or `Not` node, nor a
    `And`/`Or` of `Exists` or `Not` nodes.
    """
    if isinstance(node, (n.Exists, n.Not)):
        return False
    if isinstance(node, (n.Or, n.And)):
        return need_exists(node.children[0]) or need_exists(node.children[1])
    return True


@monkeypatch(RQLRewriter)
def _inserted_root(self, new):
    if need_exists(new):
        new = n.Exists(new)
    return new


@monkeypatch(RQLRewriter)
def remove_ambiguities(self, snippets, newsolutions):
    # the snippet has introduced some ambiguities, we have to resolve them
    # "manually"
    variantes = self.build_variantes(newsolutions)
    if not variantes:
        return newsolutions
    # insert "is" where necessary
    varexistsmap = {}
    self.removing_ambiguity = True
    for (erqlexpr, varmap, oldvarname), etype in variantes[0].items():
        varname = self.rewritten[(erqlexpr, varmap, oldvarname)]
        var = self.select.defined_vars[varname]
        exists = var.references()[0].scope
        exists.add_constant_restriction(var, 'is', etype, 'etype')
        varexistsmap[varmap] = exists
    # insert ORED exists where necessary
    for variante in variantes[1:]:
        self.insert_snippets(snippets, varexistsmap)
        for key, etype in variante.items():
            varname = self.rewritten[key]
            try:
                var = self.select.defined_vars[varname]
            except KeyError:
                # not a newly inserted variable
                continue
            exists = var.references()[0].scope
            exists.add_constant_restriction(var, 'is', etype, 'etype')
    # recompute solutions
    self.compute_solutions()
    # clean solutions according to initial solutions
    return remove_solutions(self.solutions, self.select.solutions,
                            self.select.defined_vars)


@monkeypatch(RQLRewriter)
def build_variantes(self, newsolutions):
    variantes = set()
    for sol in newsolutions:
        variante = []
        for key, var_name in self.rewritten.items():
            var = self.select.defined_vars[var_name]
            # skip variable which are only in a NOT EXISTS (mustn't be splitted)
            if len(var.stinfo['relations']) == 1 and isinstance(var.scope.parent, n.Not):
                continue
            # skip variable whose type is already explicitly specified
            if var.stinfo['typerel']:
                continue
            variante.append((key, sol[var_name]))
        if variante:
            variantes.add(tuple(variante))

    # rebuild variantes as dict
    variantes = [dict(v) for v in variantes]
    # remove variable which have always the same type
    for key in self.rewritten:
        it = iter(variantes)
        try:
            etype = next(it)[key]
        except StopIteration:
            continue
        for variante in it:
            if variante[key] != etype:
                break
        else:
            for variante in variantes:
                del variante[key]

    return variantes
