import warnings

from django.db.models import Q
from django import template
from incunafein.module.navigation.models import Navigation

register = template.Library()
class IncunaFeinNavigationNode(template.Node):
    """
    Render a navigation.
    arguments: 
        navigate: The root item (instance or dom_id) of the navigation to render.
        depth: The depth of sub navigation to include.
        show_all_subnav: Whether to show all sub navigation items (or just the ones in the currently selected branch).

    example usage:
        {% incunafein_navigation 'footer' 1 0 %}
    """
    def __init__(self,  navigate=None, depth=1, show_all_subnav=False):
        self.navigate = navigate
        self.depth = depth
        self.show_all_subnav = show_all_subnav

    def render(self, context):
        navigate = self.navigate and self.navigate.resolve(context)
        depth = int(self.depth.resolve(context) if isinstance(self.depth, template.FilterExpression) else self.depth)
        show_all_subnav = self.show_all_subnav.resolve(context) if isinstance(self.show_all_subnav, template.FilterExpression) else self.show_all_subnav

        instance = None
        if isinstance(navigate, Navigation):
            instance = navigate
        elif isinstance(navigate, (str, unicode)) and navigate:
            try:
                instance = Navigation.objects.get(dom_id=navigate)
            except Navigation.DoesNotExist, er:
                return ''

        if not 'request' in context:
            warnings.warn('No request in the context. Try using RequestContext in the view.')
            return ''
        path = context['request'].path

        try:
            current = Navigation.objects.filter(Q(url=path) | Q(page___cached_url=path))[0]
        except IndexError:
            current = None

        entries = self.entries(instance, current, depth, show_all_subnav)

        if not entries:
            return ''

        def get_item(item, next_level, extra_context=None):
            context.push()

            if extra_context:
                context.update(extra_context)

            context['item'] = item
            context['url'] = item.get_absolute_url()
            context['is_current'] = context['url'] == path
            context['title'] = unicode(item)

            css_class = item.css_class or (item.page and item.page.slug) or ''
            if css_class:
                if 'css_class' in context:
                    context['css_class'] += ' ' + css_class
                else:
                    context['css_class'] = css_class

            context['is_ancestor'] = False
            if context['is_current']:
                if 'css_class' in context:
                    context['css_class'] += ' selected'
                else:
                    context['css_class'] = 'selected'
            else:
                context['is_ancestor'] = path.startswith(context['url'])

            if next_level > item.level:
                context['down'] = next_level - item.level
            elif next_level < item.level:
                context['up'] = item.level - next_level

            html = template.loader.get_template('navigation/navitem.html').render(context)
            context.pop()

            return html

        output = ''
        item = entries[0]
        for i, next in enumerate(entries[1:]):
            output += get_item(item, next.level, {'css_class': i==0 and 'first' or ''})
            item = next
        
        output += get_item(item, entries[0].level, {'css_class': len(entries)==1 and 'first last' or 'last'})

        if instance:
            return '<ul id="%s" class="%s">%s</ul>' % (instance.dom_id, instance.css_class, output)
        else:
            return '<ul>%s</ul>' % (output,)


    def entries(self, instance, current, depth=1, show_all_subnav=False):

        if depth == 1:
            if instance is None:
                return Navigation.objects.filter(parent__isnull=True)
            else:
                return instance.children.all()
        elif show_all_subnav:
            if instance is None:
                return Navigation.objects.filter(level__lt=depth)
            else:
                return instance.get_descendants().filter(level__lt=depth)
        else:
            if instance is None:
                qs = Navigation.objects.filter(parent__isnull=True) 
                if current:
                    qs = qs | current.get_ancestors() \
                            | current.get_siblings(include_self=True).filter(level__lt=depth) \
                            | current.children.filter(level__lt=depth)
            else:
                relative_depth = instance.level + depth
                qs = instance.children.all()
                if current:
                    qs = qs | current.get_ancestors().filter(level__gt=instance.level) \
                            | current.get_siblings(include_self=True).filter(level__gt=instance.level, level__lt=relative_depth) \
                            | current.children.filter(level__gt=instance.level, level__lt=relative_depth)
            return qs

def do_incunafein_navigation(parser, token):
    args = token.split_contents()
    if len(args) > 4:
        raise template.TemplateSyntaxError("'%s tag accepts no more than 3 argument." % args[0])
    return IncunaFeinNavigationNode(*map(parser.compile_filter, args[1:]))

register.tag('incunafein_navigation', do_incunafein_navigation)


