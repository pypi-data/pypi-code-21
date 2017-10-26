#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.json.interfaces import IJSONWriter

# import local interfaces
from ztfy.baseskin.interfaces import IDialog
from ztfy.baseskin.interfaces.form import IGroupsBasedForm, IWidgetsGroup, IAJAXForm, IForm, IInnerSubForm, \
    IInnerTabForm, ICustomUpdateSubForm
from ztfy.myams.interfaces import IModalEditFormButtons, IModalAddFormButtons, IEditFormButtons, IAddFormButtons, \
    IModalDisplayFormButtons, IObjectData

# import Zope3 packages
from z3c.form import button
from z3c.formjs import ajax
from z3c.formui import form
from zope.component import getAdapters, getUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, Attributes
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.baseskin.form import FormObjectCreatedEvent, FormObjectModifiedEvent
from ztfy.utils.property import cached_property

from ztfy.myams import _


#
# Form widgets group
#

class WidgetsGroup(object):
    """Widgets group"""

    implements(IWidgetsGroup)

    def __init__(self, id, widgets=(), legend=None, help=None, css_class='', switch=False,
                 checkbox_switch=False, checkbox_field=None, hide_if_empty=False):
        assert (not checkbox_switch) or checkbox_field, "You must define checkbox field when using checkbox switch"
        self.id = id
        self.widgets = widgets
        self.legend = (legend is None) and id or legend
        self.help = help
        self._css_class = css_class
        self.switch = switch
        self.checkbox_switch = checkbox_switch
        self.checkbox_field = checkbox_field
        self.hide_if_empty = hide_if_empty

    @property
    def switchable(self):
        return self.switch or self.checkbox_switch

    @property
    def checkbox_widget(self):
        if self.checkbox_field is None:
            return None
        for widget in self.widgets:
            if widget.field is self.checkbox_field.field:
                return widget

    @cached_property
    def visible(self):
        if self.checkbox_switch:
            widget = self.checkbox_widget
            context = widget.context
            name = widget.field.getName()
            value = getattr(context, name, None)
            return bool(value)
        else:
            if not (self.switch and self.hide_if_empty):
                return True
            for widget in self.widgets:
                if not widget.ignoreContext:
                    field = widget.field
                    context = widget.context
                    name = field.getName()
                    value = getattr(context, name, None)
                    if value and (value != field.default):
                        return True
            return False

    @property
    def visible_widgets(self):
        for widget in self.widgets:
            if (self.checkbox_field is None) or (widget.field is not self.checkbox_field.field):
                yield widget

    @property
    def css_class(self):
        css_class = self._css_class
        if self.switch:
            if self.checkbox_switch:
                css_class += ' checker'
            else:
                css_class += ' switcher'
        return css_class

    @property
    def switcher_state(self):
        return 'on' if self.visible else 'off'

    @property
    def checker_state(self):
        return 'on' if self.visible else 'off'


def NamedWidgetsGroup(id, widgets, names=(), legend=None, help=None, css_class='', switch=False,
                      checkbox_switch=False, checkbox_field=None, hide_if_empty=False):
    """Create a widgets group based on widgets names"""
    return WidgetsGroup(id, [widgets.get(name) for name in names], legend, help, css_class, switch,
                        checkbox_switch, checkbox_field, hide_if_empty)


class GroupsBasedForm(object):
    """Groups based form"""

    implements(IGroupsBasedForm)

    def __init__(self):
        self._groups = []

    def addGroup(self, group):
        self._groups.append(group)

    @property
    def groups(self):
        result = self._groups[:]
        others = []
        for widget in self.widgets.values():
            found = False
            for group in result:
                if widget in group.widgets:
                    found = True
                    break
            if not found:
                others.append(widget)
        if others:
            result.insert(0, WidgetsGroup(None, others))
        return result


#
# AJAX form
#

class AjaxForm(ajax.AJAXRequestHandler):
    """Custom base class used to handle AJAX errors"""

    implements(IAJAXForm, IObjectData)

    object_data = None
    form_options = None

    def getFormOptions(self):
        if self.form_options:
            writer = getUtility(IJSONWriter)
            return writer.writer(self.form_options)

    def getAjaxErrors(self):
        errors = {'status': u'error',
                  'error_message': translate(self.status, context=self.request)}
        for error in self.errors:
            error.update()
            error = removeSecurityProxy(error)
            if hasattr(error, 'widget'):
                widget = removeSecurityProxy(error.widget)
                if widget is not None:
                    errors.setdefault('widgets', []).append({'name': widget.name,
                                                             'label': translate(widget.label, context=self.request),
                                                             'message': translate(error.message, context=self.request)})
                else:
                    errors.setdefault('messages', []).append({'message': translate(error.message, context=self.request)})
            else:
                errors.setdefault('messages', []).append(translate(error.message, context=self.request))
        return errors


#
# Base forms
#

def getFormWeight(form):
    try:
        return form.weight
    except AttributeError:
        return 0


class BaseForm(GroupsBasedForm, AjaxForm, form.Form):
    """Base add form"""

    implements(IForm)

    autocomplete = 'on'
    display_hints_on_widgets = True
    warn_on_change = u'default'
    handle_upload = False

    subforms_legend = None

    css_class = 'ams-form form-horizontal'
    label_css_class = FieldProperty(IForm['label_css_class'])
    input_css_class = FieldProperty(IForm['input_css_class'])

    callbacks = {}

    def __init__(self, context, request):
        GroupsBasedForm.__init__(self)
        form.Form.__init__(self, context, request)

    def update(self):
        form.Form.update(self)
        self.getForms()
        [subform.update() for subform in self.subforms]
        [tabform.update() for tabform in self.tabforms]

    @property
    def warnOnChange(self):
        if self.warn_on_change is True:
            return u'true'
        elif self.warn_on_change is False:
            return u'false'
        else:
            return None

    def isDialog(self):
        return IDialog.providedBy(self)

    def getForms(self, with_self=True):
        if not hasattr(self, 'subforms'):
            self.subforms = self.createSubForms()
        if not hasattr(self, 'tabforms'):
            self.tabforms = self.createTabForms()
        if with_self:
            return [self, ] + self.subforms + self.tabforms
        else:
            return self.subforms + self.tabforms

    def createSubForms(self):
        return sorted((adapter[1] for adapter in getAdapters((self, ), IInnerSubForm)), key=getFormWeight)

    def createTabForms(self):
        return sorted((adapter[1] for adapter in getAdapters((self, ), IInnerTabForm)), key=getFormWeight)

    def getWidgetCallback(self, widget):
        return self.callbacks.get(widget)

    def updateWidgets(self, prefix=None):
        form.Form.updateWidgets(self, prefix)
        self.getForms()
        [subform.updateWidgets(prefix) for subform in self.subforms]
        [tabform.updateWidgets(prefix) for tabform in self.tabforms]

    @property
    def errors(self):
        result = []
        for subform in self.getForms():
            result.extend(subform.widgets.errors)
        return result

    def updateContent(self, content, data):
        changes = form.applyChanges(self, content, data)
        self.getForms()
        for subform in self.subforms:
            if ICustomUpdateSubForm.providedBy(subform):
                updates = ICustomUpdateSubForm(subform).updateContent(content, data)
                if isinstance(updates, dict):
                    changes.update(updates)
            else:
                changes.update(form.applyChanges(subform, content, data))
        for tabform in self.tabforms:
            if ICustomUpdateSubForm.providedBy(tabform):
                updates = ICustomUpdateSubForm(tabform).updateContent(content, data)
                if isinstance(updates, dict):
                    changes.update(updates)
            else:
                changes.update(form.applyChanges(tabform, content, data))
        return changes


#
# Add forms
#

class AddForm(BaseForm, form.AddForm):
    """Base add form class"""

    buttons = button.Buttons(IAddFormButtons)

    legend = _("Add form")
    handler = '/@@ajax/ajaxCreate'
    formErrorsMessage = _("There were some errors.")

    def updateActions(self):
        form.AddForm.updateActions(self)
        if 'add' in self.actions:
            self.actions['add'].addClass('btn-primary')

    @ajax.handler
    def ajaxCreate(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            return writer.write(self.getAjaxErrors())
        result = self.createAndAdd(data)
        self.request.response.setHeader('Content-Type', 'text/plain; charset=utf-8')
        return self.getSubmitOutput(writer, result)

    def createAndAdd(self, data):
        object = self.create(data)
        notify(ObjectCreatedEvent(object))
        self.add(object)
        self.updateContent(object, data)
        notify(FormObjectCreatedEvent(object, self))
        return object

    def getSubmitOutput(self, writer, changes):
        return writer.write({'status': 'reload',
                             'location': self.nextURL()})


class DialogAddForm(AddForm):
    """Base dialog add form"""

    implements(IDialog)

    buttons = button.Buttons(IModalAddFormButtons)
    dialog_class = 'modal-medium'


#
# Edit forms
#

class EditForm(BaseForm, form.EditForm):
    """Base edit form class"""

    buttons = button.Buttons(IEditFormButtons)

    legend = _("Edit form")
    handler = '/@@ajax/ajaxEdit'
    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    def updateActions(self):
        form.EditForm.updateActions(self)
        if 'submit' in self.actions:
            self.actions['submit'].addClass('btn-primary')

    @ajax.handler
    def ajaxEdit(self):
        return self.handleApply()

    def handleApply(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            return writer.write(self.getAjaxErrors())
        changes = self.applyChanges(data)
        self.request.response.setHeader('Content-Type', 'text/plain; charset=utf-8')
        return self.getSubmitOutput(writer, changes)

    def applyChanges(self, data):
        content = self.getContent()
        changes = self.updateContent(content, data)
        if changes:
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(Attributes(interface, *names))
            notify(FormObjectModifiedEvent(content, self, *descriptions))
        return changes

    def getSubmitOutput(self, writer, changes):
        if changes:
            message = self.successMessage
        else:
            message = self.noChangesMessage
        return writer.write({'status': 'success',
                             'message': translate(message, context=self.request)})


class DialogEditForm(EditForm):
    """Base dialog edit form"""

    implements(IDialog)

    buttons = button.Buttons(IModalEditFormButtons)
    dialog_class = 'modal-medium'


#
# Display forms
#

class DisplayForm(BaseForm, form.DisplayForm):
    """Base display form class"""


class DialogDisplayForm(DisplayForm):
    """Base dialog display form"""

    implements(IDialog)

    buttons = button.Buttons(IModalDisplayFormButtons)
    dialog_class = 'modal-medium'
