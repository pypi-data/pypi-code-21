from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

def is_mptt(m):
    # Does it quack?
    return bool(getattr(m._meta, 'tree_id_attr', False) \
                 and getattr(m._meta, 'parent_attr', False) \
                 and getattr(m._meta, 'left_attr', False) \
                 and getattr(m._meta, 'right_attr', False) \
                 and getattr(m._meta, 'level_attr', False))

class MPTTFilterSpec(RelatedFilterSpec):
    def __init__(self, f, request, params, model, model_admin, field_path=None, **kwargs):
        from feincms.utils import shorten_string

        super(MPTTFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)

        if getattr(self, 'field_path', None) is None:
            self.field_path = f.name

        to = f.rel.to
        opts = to._meta

        mppt_lookups = {opts.tree_id_attr: '%s__exact' % (opts.tree_id_attr), 
                        opts.left_attr: '%s__gte' % (opts.left_attr), 
                        opts.right_attr: '%s__lte' % (opts.left_attr)}

        parents = to.objects.all()
        if self.field_path == opts.parent_attr:
            parent_id = "%s__id" % opts.parent_attr
            parent_ids = to.objects.exclude(parent=None).values_list(parent_id, flat=True).order_by(parent_id).distinct()
            parents = parents.filter(pk__in=parent_ids)
            self.title_suffix = ''
        else:
            self.title_suffix = ' ' + unicode(super(MPTTFilterSpec, self).title())
            for k, v in mppt_lookups.items():
                mppt_lookups[k] = "%s__%s" % (self.field_path, v)


        self.lookup_kwargs = mppt_lookups.values()
        self.lookup_params = dict([(k, request.GET.get(k, None)) for k in self.lookup_kwargs])
        self.lookup_choices = [("%s%s" % ("&nbsp;" * getattr(parent, opts.level_attr), shorten_string(unicode(parent), max_length=25)), 
                                dict([(lookup, str(getattr(parent, kwarg))) for kwarg,lookup in mppt_lookups.items()]))
                               for parent in parents]

    def choices(self, cl):
        yield {
            'selected':     self.lookup_params == dict([(k, None) for k in self.lookup_kwargs]),
            'query_string': cl.get_query_string({}, self.lookup_kwargs),
            'display':      _('All')
        }

        for title, param_dict in self.lookup_choices:
            yield {
                'selected':     param_dict == self.lookup_params,
                'query_string': cl.get_query_string(param_dict),
                'display':      mark_safe(smart_unicode(title))
            }


    def title(self):
        return _('Ancestor') + self.title_suffix


# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: bool(f.rel) and is_mptt(f.rel.to), MPTTFilterSpec))
#FilterSpec.register(lambda f: bool(f.rel) and is_mptt(f.rel.to), 
#                    MPTTFilterSpec)

