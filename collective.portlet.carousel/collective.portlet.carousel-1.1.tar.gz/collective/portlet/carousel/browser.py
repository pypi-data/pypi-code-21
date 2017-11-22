
from interfaces import ICarouselPortlet
from portlet import CarouselPortletAssignment
from i18n import MessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.app.portlets.browser import z3cformhelper
from plone.memoize.view import memoize

from z3c.form import field

script = """
jQuery(function($){
  rotate = %(rotate)s;
  var timeout;

  next = function(index, auto) {
    clearTimeout(timeout);
    x = parseInt(index);
    p = $('.portletCarousel ul li');
    i = $('.portletCarousel dl dd.carouselPortletItem');
    p.removeClass('current');
    i.removeClass('current').animate({opacity:0});
    i.hide();
    x%%=i.length;
    ci = i.eq(x);
    cp = p.eq(x);
    cp.addClass('current');
    ci.addClass('current').animate({opacity:1});
    ci.show();
    if(auto) {
      timeout = setTimeout("next("+(++x)+", " + auto + ")", %(timeout)d);
    }
  }

  $('.portletCarousel ul li').click(function(){
    cp = $(this);
    if (cp.is('.current'))
      return false;
    x = cp.index('.portletCarousel ul li');
    next(x, true);
    return false;
  });

  if (rotate) {
    $(document).ready(function() {
      timeout = setTimeout("next(1,true)", %(timeout)d);
    });
  }

});


"""


class CarouselPortletRenderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')

    @property
    def title(self):
        return self.data.title

    @property
    def available(self):
        return self.data.collection_reference or \
            len(self.data.references) > 0

    @property
    def omit_border(self):
        return self.data.omit_border

    @property
    def rotate(self):
        return self.data.automatic_rotation and \
            len(self.items()) > 1 and self.timeout > 0

    @property
    def timeout(self):
        return self.data.timeout * 1000

    @memoize
    def items(self):
        items = []

        collection = None
        if self.data.collection_reference:
            collection = self.data.collection_reference.to_object

        if collection:
            resf = hasattr(collection, 'results') and \
                collection.results or collection.queryCatalog
            for brain in resf():
                items.append(brain.getObject())
        else:
            references = self.data.references
            for reference in references:
                items.append(reference.to_object)

        if hasattr(self.data, 'limit') and self.data.limit > 0:
            return items[:self.data.limit]

        return items

    def script(self):
        return script % dict(rotate=self.rotate and 'true' or 'false',
                             timeout=self.timeout)


class CarouselPortletAddForm(z3cformhelper.AddForm):
    fields = field.Fields(ICarouselPortlet)
    label = _(u"Add carousel portlet")

    def create(self, data):
        return CarouselPortletAssignment(**data)


class CarouselPortletEditForm(z3cformhelper.EditForm):
    fields = field.Fields(ICarouselPortlet)
    label = _(u"Edit carousel portlet")
