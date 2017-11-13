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

"""cubicweb-datacat geo-spatial views/forms/actions/components"""

import io

# XXX: find a way to load Postgis WKB from osgeo.ogr and thus avoid to depends
# on shapely in addition to osgeo
from shapely import wkb

from logilab.mtconverter import xml_escape
from rql import nodes

from cubicweb import _
from cubicweb.predicates import (
    adaptable,
    is_instance,
)
from cubicweb.utils import (
    json_dumps,
    JSString,
    make_uid,
)
from cubicweb import tags
from cubicweb.web import (
    component,
    facet as cwfacet,
    formwidgets,
    htmlwidgets,
    ProcessFormError,
)
from cubicweb.web.views import (
    primary,
    uicfg,
)

from cubes.datacat.geoutils import merge_in_geojson_collection
from cubes.leaflet import views as leafletviews


affk = uicfg.autoform_field_kwargs
afs = uicfg.autoform_section
pvs = uicfg.primaryview_section


#
# Leaflet maps and views
#
#

class LeafletJSONPropertiesMap(leafletviews.LeafletMultiPolygonValues):
    """Leaflet map for plotting GeoJSON data and associated properties.

    Unlike parent class, this one computes initial zoom in order to fit data at loading time.

    Should be used in a view.
    """
    # See https://www.cubicweb.org/ticket/5630012
    # TODO: drop this class when ticket is done

    default_settings = {
        'legend_visibility': False,
        'info_visibility': True,
        'info_position': 'topright',
    }

    js_plotter = 'cw.cubes.datacat.plotMapProperties'


class LeafletGeoJSONEntityView(leafletviews.AbstractLeafletView):
    """Plot IGeoJSON adaptable entities in a Leaflet map."""

    __regid__ = 'leaflet-geojson-entities'
    __select__ = leafletviews.AbstractLeafletView.__select__ & adaptable('IGeoJSON')

    plotclass = LeafletJSONPropertiesMap

    def call(self, *args, **kwargs):
        self._cw.add_js('cubes.datacat.js')
        super(LeafletGeoJSONEntityView, self).call(*args, **kwargs)

    def build_markers(self):
        """Build the GeoJSON data from entities in the view."""
        geojsons = (entity.cw_adapt_to('IGeoJSON').as_geojson()
                    for entity in self.cw_rset.entities())
        data = merge_in_geojson_collection(geojsons)
        return JSString(json_dumps(data))


class DrawableLeafletJsonMap(leafletviews.LeafletMultiPolygon):
    """Leaflet map for plotting GeoJSON data and allowing draws

    Unlike parent class, this one computes initial zoom in order to fit data at loading time.

    Should be used in a view.
    """

    default_settings = leafletviews.LeafletMultiPolygon.default_settings.copy()
    default_settings.update({
        'draw_settings': {
            'polyline': {},
            'polygon': {},
            'rectangle': {},
            'circle': {},
            'marker': {},
        },
        'edit_settings': {
            'edit': {},
            'remove': {},
        }
    })
    js_plotter = 'cw.cubes.datacat.plotDrawableMap'

    def render(self, req, datasource, use_cdn=True):
        """Renders the map."""
        # Need to call the parent method first because Leaflet.Draw needs Leaflet which is loaded
        # in parent view
        div_holder = super(DrawableLeafletJsonMap, self).render(req, datasource, use_cdn=use_cdn)
        req.add_js('cubes.datacat.js')
        if use_cdn:
            req.add_css(
                'https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/0.2.3/leaflet.draw.css',
                localfile=False)
            req.add_js(
                'https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/0.2.3/leaflet.draw.js',
                localfile=False)
        else:
            req.add_css('leaflet.draw.css')
            req.add_js('leaflet.draw.js')
        return div_holder


class DrawableLeafletJsonView(leafletviews.GeoJsonView):
    """View for plotting GeoJSON data in an drawable Leaflet map."""

    __regid__ = 'leaflet-geojson-draw'

    plotclass = DrawableLeafletJsonMap


class GeoJSONEntityCtxComponent(component.EntityCtxComponent):
    """Display geospatial data in a Leaflet view."""
    __regid__ = 'datacat.geojson-entity-component'
    __select__ = component.EntityCtxComponent.__select__ & adaptable('IGeoJSON')
    title = _('Location')
    context = 'navcontentbottom'

    def render_body(self, w):
        self._cw.view('leaflet-geojson-entities', rset=self.entity.as_rset(), w=w)


class FacetGeoJSONWidget(htmlwidgets.HTMLWidget):
    """Map widget to be used in a facet."""

    default_settings = {
        'width': '300px',
        'height': '300px',
        'drawSettings': {},
        'editSettings': {},
    }

    def __init__(self, facet, rset, leaflet_vid='leaflet-geojson-draw', custom_settings=None):
        self.facet = facet
        self.rset = rset
        self.leaflet_vid = leaflet_vid
        self.geojsonpolygon = facet._cw.form.get(xml_escape(facet.__regid__) + 'Input')
        # Map settings
        self.settings = self.default_settings.copy()
        self.settings.update(custom_settings or {})

    @property
    def height(self):
        """Height of the widget"""
        return 4.5

    def _render(self):
        """Render the widget as a Leaflet Map."""
        w = self.w
        facet = self.facet
        cnx = facet._cw
        # Useful vars
        facettitle = xml_escape(facet.title)
        facetname = xml_escape(facet.__regid__)
        inputname = facetname + 'Input'
        divid = make_uid('mapFacet')
        facetid = make_uid(facet.__regid__)
        self.settings.update({'divid': divid, 'inputName': inputname})
        w(u'<div id="{}" class="facet">\n'.format(facetid))  # Facet opening <div>
        # Facet title
        cssclass = 'facetTitle' if not facet.allow_hide else 'facetTitle hideFacetBody'
        w(u'<div class="{}" cubicweb:facetName="{}">{}</div>\n'.format(
            cssclass, facetname, facettitle))
        # Facet body
        cssclass = 'facetBody' if facet.start_unfolded else 'facetBody hidden'
        w(u'<div class="{}">\n'.format(cssclass))  # Facet body opening <div>
        cnx.view(self.leaflet_vid, rset=self.rset, w=w, custom_settings=self.settings)
        w(u'<input type="hidden" name="{}" value="{}" />\n'.format(
            inputname, self.geojsonpolygon or u''))
        w(u'</div>\n')  # Facet body closing </div>
        w(u'</div>\n')  # Facet closing </div>


#
# GeoJSON facet
#

class RelationExtentFacet(cwfacet.AbstractFacet):
    """Base facet to filter an entity list according to a geospatial intersection criteria on other
    entities to which they are related.

    This facet displays a geographical map with the extent (that is, the convex hull) of all the
    related entities. We can draw polygons in this map to retain only entities who intersect the
    drawn polygons.

    Attributes to be declared for this facet are the same as for
    :class:`cwfacet.RelationAttributeFacet`.

    For example, let us consider a schema where offices are related to cities, and cities have a
    geometry attribute:

    .. code-block: python

        class City(EntityType):
            name = String(description='City name')
            geometry = Geometry(description='City geospatial location',
                                geom_type='MULTIPOLYGON', srid=4326, coord_dimension=2)

        class Office(EntityType):
            name = String(description='Office name')
            in_city = SubjectRelation('City', cardinality='1?')

    With this schema, we can define a facet to filter offices according to their city geometry:

    .. code-block: python

        class OfficeCityGeometryFacet(RelationExtentFacet):
            __regid__ = 'office_city_geom_facet'
            __select__ = is_instance('Office')
            rtype = 'in_city'
            role = 'subject'
            target_attr = 'geometry'

    Then in the web interface, when we are displaying a list of offices, we see a map among the
    facets. This map shows us the extent of all cities related to offices in the list. We can draw
    polygons on this map: this will select only cities that intersect the polygons, and consequently
    only offices that are related to the selected cities will remain.
    """

    target_type = None
    target_attr_type = 'Geometry'
    title = property(cwfacet.rtype_facet_title)

    default_settings = {
        'drawSettings': {
            'polyline': False,
            'marker': False,
            'circle': False,
        },
    }

    @property
    def wdgclass(self):
        """The widget's class that will be used to display the facet."""
        return FacetGeoJSONWidget

    def get_widget(self):
        """Return the widget to be used to display the convex hull, or ``None`` if there is no
        convex hull.
        """
        rset = self._geojson_convex_hull_rset()
        if rset:
            return self.wdgclass(self, rset, custom_settings=self.default_settings)
        return None

    def add_rql_restrictions(self):
        """Add an ``ST_INTERSECTS`` restriction with geometries drawn in the widget.

        Namely, add an intersection filter (``ST_INTERSECTS(G, <drawn_polygons>)``) to select
        entities that intersect the drawn geometries.
        """
        select = self.select
        # Geometry RQL node for drawn polygons
        # (eg. ST_COLLECTIONEXTRACT(ST_GEOMFROMGEOJSON(<drawngeojsonstr>), 3))
        # Note that we must extract Polygons since Leaflet widget returns GeometryCollection
        geojsonstr = self._cw.form.get(xml_escape(self.__regid__) + 'Input')
        if not geojsonstr:
            return
        select.set_distinct(True)
        drawnvar = nodes.Constant(geojsonstr, 'String')
        geomfromjsonf = nodes.Function('ST_GEOMFROMGEOJSON')
        geomfromjsonf.append(drawnvar)
        drawnnode = nodes.Function('ST_COLLECTIONEXTRACT')
        drawnnode.append(geomfromjsonf)
        drawnnode.append(nodes.Constant(3, 'Int'))
        # Target geometry RQL node for entities (eg. G WHERE E geometry G, E related X)
        targetvar = self._restriction_geometry_variable()
        # Target geometry type (eg. MultiPolygon)
        target_geomtype = self._target_geom_type()
        # List all possible intersections: Polygon/Point, Polygon/Line, Polygon/Polygon
        intersectnodes = []
        for entitynode in self._intersect_operand(targetvar, target_geomtype):
            intersectf = nodes.Function('ST_INTERSECTS')
            intersectf.append(drawnnode)
            intersectf.append(entitynode)
            comp = nodes.Comparison('=', intersectf)
            comp.append(nodes.Constant('True', 'Boolean'))
            intersectnodes.append(comp)
        # OR all intersections and insert in HAVING clause
        for i, intersectnode in enumerate(intersectnodes):
            if i == 0:
                havingnode = intersectnode
            else:
                havingnode = nodes.Or(havingnode, intersectnode)
        having = select.having
        if not having:
            select.set_having([havingnode])
        else:
            select.replace(having[0], nodes.And(havingnode, having[0]))

    def _geojson_convex_hull_rset(self):
        """Return a one-cell result set: the convex hull of all selected entities in GeoJSON."""
        select = self.select
        select.save_state()
        try:
            cwfacet.cleanup_select(select, self.filtered_variable)
            geomvar = self._convex_hull_geometry_variable()
            select_collectf = nodes.Function('ST_COLLECT')
            select_collectf.append(nodes.VariableRef(geomvar))
            # Restrict to non-empty ST_COLLECT(<geomvar>) because otherwise the
            # result set would not be empty in case no entity has a location
            # with a non-empty geometry.
            # (See http://postgis.net/docs/ST_Collect.html ST_COLLECT is an
            # aggregate function.)
            having_collectf = nodes.Function('ST_COLLECT')
            having_collectf.append(nodes.VariableRef(geomvar))
            comp = nodes.Comparison('!=')
            comp.append(having_collectf)
            # Comparing to NULL does not work properly so compare with empty
            # string.
            comp.append(nodes.Constant('', 'String'))
            select.set_having([comp])
            convexhullf = nodes.Function('ST_CONVEXHULL')
            convexhullf.append(select_collectf)
            asgeojsonf = nodes.Function('ST_ASGEOJSON')
            asgeojsonf.append(convexhullf)
            select.add_selected(asgeojsonf)
            try:
                return self.rqlexec(select.as_string(), self.cw_rset.args)
            except Exception:
                self.exception('Error while parsing values for {} (rql: "{}")'.format(
                    self, select.as_string()))
                return ()
        finally:
            select.recover()
        return None

    def _convex_hull_geometry_variable(self):
        """Return a RQL variable representing the Geometry attribute to be used for computing convex
        hull."""
        var = cwfacet.insert_attr_select_relation(self.select, self.filtered_variable, self.rtype,
                                                  self.role, self.target_attr, sortasc=None)
        if self.target_type is not None:
            self.select.add_type_restriction(var, self.target_type)
        # var represent target entity, we want geometry attribute on the target entity
        for varref in self.select.selection[:]:
            if varref.variable != var:
                geomvar = varref.variable
            self.select.remove_selected(varref)
        return geomvar

    def _restriction_geometry_variable(self):
        """Return a RQL variable representing the target Geometry attribute to be used in the added
        RQL restriction."""
        filtered_variable = self.filtered_variable
        # Add X rtype E (or E rtype X) restriction (E: related entity with geometry attribute)
        relentityvar = self.select.make_variable()
        if self.role == 'subject':
            rel = nodes.make_relation(filtered_variable, self.rtype, (relentityvar,),
                                      nodes.VariableRef)
        else:
            rel = nodes.make_relation(relentityvar, self.rtype, (filtered_variable,),
                                      nodes.VariableRef)
        self.select.add_restriction(rel)
        # Add E target_attr G restriction to query (G: target Geometry attribute)
        geomvar = self.select.make_variable()
        geomrel = nodes.make_relation(relentityvar, self.target_attr, (geomvar,),
                                      nodes.VariableRef)
        self.select.add_restriction(geomrel)
        return geomvar

    def _target_geom_type(self):
        """Return the geometry type of the target attribute."""
        rschema = self._cw.vreg.schema.rschema(self.target_attr)
        rdef = rschema.rdefs.itervalues().next()  # XXX: if multiple attr with same name exists ?
        return rdef.geom_type

    def _intersect_operand(self, var, geom_type):
        """Yield in turn each RQL node to be used as an operand in the ``ST_INTERSECTS`` function.

        For example, if ``G ``is an RQL variable representing a ``Geometry`` attribute with
        ``geom_type`` ``MultiPolygon``, then it will yield only G.

        Things get complicated when ``geom_type`` is ``GeometryCollection``. Since Postgis
        ``ST_INTERSECTS`` function does not work with geometry collections, we must extract each
        geometry type (``1: Point, 2: LineString, 3: Polygon``) and yield each one in turn.
        """
        # ST_Intersect refuses GeometryCollection (http://postgis.net/docs/ST_Intersects.html)
        if 'GEOMETRYCOLLECTION' not in geom_type.upper():
            yield var
        else:
            for i in range(1, 4):  # http://postgis.net/docs/ST_CollectionExtract.html
                extractf = nodes.Function('ST_COLLECTIONEXTRACT')
                extractf.append(var)
                extractf.append(nodes.Constant(i, 'Int'))
                yield extractf


class ExtentFacet(RelationExtentFacet):
    """Base facet to filter an entity list according to a geospatial intersection criteria.

    This facet displays a geographical map with the extent (that is, the convex hull) of all the
    entities. We can draw polygons in this map to retains only entities which intersect the drawn
    polygons.

    Attributes to be declared for this facet are the same as for :class:`cwfacet.AttributeFacet`.

    For example, let us consider a schema where offices have a geometry attribute:

    .. code-block: python

        class Office(EntityType):
            name = String(description='Office name')
            geometry = Geometry(description='Office geospatial shape',
                                geom_type='MULTIPOLYGON', srid=4326, coord_dimension=2)

    With this schema, we can define a facet to filter offices according to their geometries:

    .. code-block: python

        class OfficeGeometryFacet(ExtentFacet):
            __regid__ = 'office_geom_facet'
            __select__ = is_instance('Office')
            rtype = 'geometry'

    Then in the web interface, when we are displaying a list of offices, we see a map among the
    facets. This map shows us the extent of all offices in our list. We can draw polygons on this
    map: this will select only offices that intersect the drawn polygons.
    """

    role = 'subject'

    def _convex_hull_geometry_variable(self):
        """Return a RQL variable representing the Geometry attribute to be used for computing convex
        hull."""
        return cwfacet._add_rtype_relation(self.select, self.filtered_variable, self.rtype,
                                           self.role)[0]

    def _restriction_geometry_variable(self):
        """Return a RQL variable representing the target Geometry attribute to be used in the added
        RQL restriction."""
        filtered_variable = self.filtered_variable
        # Add X rtype G restriction (G: target Geometry attribute)
        geomvar = self.select.make_variable()
        geomrel = nodes.make_relation(filtered_variable, self.rtype, (geomvar,), nodes.VariableRef)
        self.select.add_restriction(geomrel)
        return geomvar

    def _target_geom_type(self):
        """Return the geometry type of the target attribute."""
        rschema = self._cw.vreg.schema.rschema(self.rtype)
        rdef = rschema.rdefs.itervalues().next()  # XXX: if multiple attr with same name exists ?
        return rdef.geom_type


class DatasetGeometryFacet(RelationExtentFacet):
    __regid__ = 'datacat.dataset_extent_facet'
    __select__ = is_instance('Dataset')
    rtype = 'locate_datasets'
    role = 'object'
    target_attr = 'geometry'


class LocationGeometryFacet(ExtentFacet):
    __regid__ = 'datacat.location_extent_facet'
    __select__ = is_instance('Location')
    rtype = 'geometry'


#
# Location
#


class LongitudeLatitudeWidget(formwidgets.TextInput):
    """Form widget handling POINT(x y) geometry attribute as longitude and
    latitude.
    """

    def _render(self, form, field, renderer):
        ustring = io.StringIO()
        w = ustring.write
        value = self.values(form, field)[0]
        longitude = 0
        latitude = 0
        if value:
            value = wkb.loads(value.decode('hex'))
            if not len(value) == 1:
                raise ValueError('cannot render {} in form widget'.format(value))
            point = value[0]
            longitude = point.x
            latitude = point.y

        for label, value in [(u'longitude', longitude),
                             (u'latitude', latitude)]:
            w(u'<div class="form-group">')
            w(tags.label(label))
            w(tags.input(type='text', value=value,
                         name=field.input_name(form, label)))
            w(u'</div>')

        return ustring.getvalue()

    def process_field_data(self, form, field):
        posted = form._cw.form
        longitude = posted.get(field.input_name(form, 'longitude')).strip() or None
        latitude = posted.get(field.input_name(form, 'latitude')).strip() or None
        msg = form._cw._(
            'both latitude and longitude must be specified on unspecified')
        if latitude is None:
            if longitude is not None:
                raise ProcessFormError(msg)
            return None
        if longitude is None:
            if latitude is not None:
                raise ProcessFormError(msg)
            return None
        return u'GEOMETRYCOLLECTION (POINT(%s %s))' % (longitude, latitude), 4326


# Hide geom by default (binary content)
pvs.tag_attribute(('Location', 'geometry'), 'hidden')
affk.tag_attribute(('Location', 'geometry'),
                   {'widget': LongitudeLatitudeWidget})


class LocationPrimaryView(primary.PrimaryView):
    """Override primary view for Location entities."""
    __select__ = primary.PrimaryView.__select__ & is_instance('Location')

    def render_entity_attributes(self, entity):
        super(LocationPrimaryView, self).render_entity_attributes(entity)
        self.wview('leaflet-geojson-entities', rset=entity.as_rset())
