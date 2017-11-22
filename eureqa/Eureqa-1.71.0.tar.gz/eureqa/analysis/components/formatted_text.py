import string
from base import _Component

def _gen_component_reference_str(component_id):
    return '<nutonian-component id="{0}" />'.format(component_id)

class _ComponentFormatter(string.Formatter):
    def __init__(self, set_component_id_func, dry_run = False):
        self._dry_run = dry_run
        self._component_definitions = []
        self._set_component_id = set_component_id_func

    def format_field(self, value, format_spec):
        if not isinstance(value, _Component):
            raise TypeError("Argument to format must be a Component")

        # keep track of all the components we have been asked to format
        comp_obj = value
        self._set_component_id(comp_obj)
        self._component_definitions.append(comp_obj._to_json())

        # replace the value to be formatted to a component reference and call parent class implementation
        new_value = _gen_component_reference_str(comp_obj._component_id)
        if self._dry_run:
            del comp_obj._component_id
        return super(_ComponentFormatter, self).format_field(new_value, format_spec)

def _set_component_id_via_placeholder(comp_obj):
    comp_obj._component_id = 'comp_id_placeholder'

class _SetComponentIDViaAnalysis(object):
    def __init__(self, analysis):
        self._analysis = analysis

    def __call__(self, comp_obj):
        comp_obj._associate(self._analysis)

class _SetComponentIDViaTable(object):
    def __init__(self, analysis):
        self._analysis = analysis

    def __call__(self, comp_obj):
        comp_obj._associate_with_table(self._analysis)

class FormattedText(object):
    """ Creates a formatted string, substituing format specifications with component references.

    For example::

        FormattedText("Tooltip {0}", Tooltip(html='Here', tooltip='this is the tooltip'))

    :param str format_str: The string to format


    """

    def __init__(self, format_str, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._format_str = format_str

        # Dry run the format in the c'tor so the format string is checked at construction time
        fmt = _ComponentFormatter(_set_component_id_via_placeholder, dry_run = True)
        self._component_references  = fmt.format(self._format_str, *self._args, **self._kwargs)
        self._component_definitions = fmt._component_definitions

    def _get_component_ref_and_defs(self, analysis, associate_with_analysis):
        if associate_with_analysis:  # only need to re-format if analysis is provided
            set_component_id_via_analysis = _SetComponentIDViaAnalysis(analysis)
            fmt = _ComponentFormatter(set_component_id_via_analysis)
            self._component_references  = fmt.format(self._format_str, *self._args, **self._kwargs)
            self._component_definitions = fmt._component_definitions
        else:
            set_component_id_via_table = _SetComponentIDViaTable(analysis)
            fmt = _ComponentFormatter(set_component_id_via_table)
            self._component_references  = fmt.format(self._format_str, *self._args, **self._kwargs)
            self._component_definitions = fmt._component_definitions

        return self._component_references, self._component_definitions

def _get_component_ref_and_defs_for_value(rendered_value, analysis, associate_with_analysis=True):
    if isinstance(rendered_value, _Component):
        comp = rendered_value
        if associate_with_analysis:
            comp._associate(analysis)
            comp_json = [comp._to_json()]
        else:
            comp_json = comp._associate_with_table(analysis)
        return _gen_component_reference_str(comp._component_id), comp_json
    elif isinstance(rendered_value, FormattedText):
        return rendered_value._get_component_ref_and_defs(analysis, associate_with_analysis)
    else:
        return rendered_value, []
