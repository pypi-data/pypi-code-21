# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb import tags
from cubicweb.predicates import is_instance

try:
    from cubes.relationwidget import views as rwdg
except ImportError:
    pass
else:

    class SearchForRelatedConceptsView(rwdg.SearchForRelatedEntitiesView):
        """Specializes relation widget to link to concepts which are expected to be constrained by
        an RQL expression on the edited relation definition.

        It will attempt to select the best suited language for display an return properly
        prefetched/ordered concepts. It's also expected that all concepts will provide a preferred
        label for the selected language (among those defined in the scheme).
        """
        __select__ = (rwdg.SearchForRelatedEntitiesView.__select__
                      & rwdg.edited_relation(tetype='Concept'))

        has_creation_form = False

        def linkable_rset(self):
            """Return rset of entities to be displayed as possible values for the
            edited relation. You may want to override this.
            """
            baserql, args = self.constrained_rql()
            # detect language first
            languages = set(lang for lang, in self._cw.execute(
                'DISTINCT Any OLC WHERE ' + baserql + ', O preferred_label OL, '
                'OL language_code OLC', args))
            for lang in self.preferred_languages():
                if lang in languages:
                    break
            else:
                if not languages:
                    return self._cw.empty_rset()
                lang = languages.pop()
            # now build the query to prefetch/sort on the preferred label in the proper language
            args['lang'] = lang
            return self._cw.execute(
                'DISTINCT Any O,OL,OLL ORDERBY OLL WHERE ' + baserql + ', O preferred_label OL, '
                'OL label OLL, OL language_code %(lang)s', args)

        def constrained_rql(self):
            constraints = self.schema_rdef.constraints
            assert len(constraints) == 1
            baserql = constraints[0].expression
            return baserql, {}

        @property
        def schema_rdef(self):
            rtype, tetype, role = self.rdef
            entity = self.compute_entity()
            return entity.e_schema.rdef(rtype, role, tetype)

        def preferred_languages(self):
            """Return language by order of preference."""
            return (self._cw.lang, 'en', None)

        @staticmethod
        def pref_label_label(concept):
            return concept.cw_rset[concept.cw_row][2]

        @staticmethod
        def pref_label_column(w, concept):
            w(tags.a(SearchForRelatedConceptsView.pref_label_label(concept),
                     href=concept.absolute_url()))

    class SelectConceptEntitiesTableView(rwdg.SelectEntitiesTableView):
        """Table view of the selectable entities in the relation widget

        Selection of columns (and respective renderer) can be overridden by
        updating `columns` and `column_renderers` class attributes.
        """
        __select__ = (rwdg.SelectEntitiesTableView.__select__ & is_instance('Concept'))

        column_renderers = rwdg.SelectEntitiesTableView.column_renderers.copy()
        # speed-up things by considering rset shape from ContainedSearchForRelatedEntitiesView
        column_renderers['entity'] = rwdg.SelectMainEntityColRenderer(
            sortfunc=SearchForRelatedConceptsView.pref_label_label,
            renderfunc=SearchForRelatedConceptsView.pref_label_column)
