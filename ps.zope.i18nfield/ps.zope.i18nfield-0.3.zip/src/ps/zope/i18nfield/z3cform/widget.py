# -*- coding: utf-8 -*-
"""I18N widget for z3c.form."""

# python imports
from copy import copy
import json

# zope imports
from persistent.dict import PersistentDict
from plone.memoize.view import memoize
from z3c.form.browser import (
    text,
    textarea,
)
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.interfaces import (
    NO_VALUE,
    IDataConverter,
    IFieldWidget,
    IFormLayer,
)
from z3c.form.widget import (
    FieldWidget,
    Widget,
)
from zope.component import (
    adapter,
    queryUtility,
)
from zope.i18n import translate
from zope.interface import (
    implementer,
    implementsOnly,
)
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import (
    IPublishTraverse,
    NotFound,
)
from zope.security.proxy import removeSecurityProxy

# local imports
from ps.zope.i18nfield import (
    interfaces,
    storage,
    utils,
)
from ps.zope.i18nfield.i18n import _
from ps.zope.i18nfield.z3cform.interfaces import (
    II18NTextAreaWidget,
    II18NTextWidget,
    II18NWidget,
)


class I18NWidgetProperty(object):
    """Base class for I18N widgets properties."""

    def __init__(self, name):
        self.__name = name

    def __get__(self, instance, klass):
        return instance.__dict__.get(self.__name, None)

    def __set__(self, instance, value):
        instance.__dict__[self.__name] = value
        for widget in instance.widgets.values():
            setattr(widget, self.__name, value)


class I18NWidget(HTMLFormElement, Widget):
    """Base class for all I18N widgets."""
    implementsOnly(II18NWidget)

    default_widget = None
    show_label = True
    default_label = _(u'Default')
    default_info = _(
        u'Please copy the default text to the corresponding language.'
    )
    option_select_language = _(u'Select language')
    button_add_language = _(u'Add translation')

    # IHTMLCoreAttributes properties
    klass = 'i18n-widget'
    style = I18NWidgetProperty('style')
    # IHTMLEventsAttributes properties
    onclick = I18NWidgetProperty('onclick')
    ondblclick = I18NWidgetProperty('ondblclick')
    onmousedown = I18NWidgetProperty('onmousedown')
    onmouseup = I18NWidgetProperty('onmouseup')
    onmouseover = I18NWidgetProperty('onmouseover')
    onmousemove = I18NWidgetProperty('onmousemove')
    onmouseout = I18NWidgetProperty('onmouseout')
    onkeypress = I18NWidgetProperty('onkeypress')
    onkeydown = I18NWidgetProperty('onkeydown')
    onkeyup = I18NWidgetProperty('onkeyup')
    # IHTMLFormElement properties
    disabled = I18NWidgetProperty('disabled')
    tabindex = I18NWidgetProperty('tabindex')
    onfocus = I18NWidgetProperty('onfocus')
    onblur = I18NWidgetProperty('onblur')
    onchange = I18NWidgetProperty('onchange')

    def __init__(self, request):
        super(I18NWidget, self).__init__(request)

    def available_languages(self):
        if self.value and self.value.keys():
            langs = self.value.keys()
            if storage.KEY_DEFAULT in langs and len(langs) == 1:
                langs.append(utils.get_language(request=self.request))
            return langs
        return [self.current()]

    def addable_languages(self):
        languages = self.languages()
        sorted_langs = self.sorted_languages()
        available_langs = self.available_languages()
        result = [
            {'lang': str(l), 'name': languages.get(l)}
            for l in sorted_langs
            if l not in available_langs
        ]
        return json.dumps(result)

    @memoize
    def sorted_languages(self):
        available = utils.available_languages()
        tmp_languages = sorted([unicode(key) for key in available])
        languages = []
        if u'en' in tmp_languages:
            tmp_languages.remove(u'en')
            languages.append(u'en')
        if u'es' in tmp_languages:
            tmp_languages.remove(u'es')
            languages.append(u'es')
        languages.extend(tmp_languages)
        return languages

    @memoize
    def languages(self):
        utility = queryUtility(interfaces.ILanguageAvailability)
        if utility is None:
            return None
        return dict(utility.getLanguageListing())

    def current(self):
        lang = utils.get_language(request=self.request)
        if self.value is not None:
            has_default = storage.KEY_DEFAULT in self.value
            return has_default and storage.KEY_DEFAULT or lang
        return lang

    def default_value(self):
        if self.value is not None:
            return self.value.get(storage.KEY_DEFAULT, None)

    def update(self):
        super(I18NWidget, self).update()
        widgets = self.widgets = {}
        langs = self.sorted_languages()
        for lang in langs:
            widget = widgets[lang] = self.default_widget(self.request)
            self.initWidget(widget, lang)
        for lang in langs:
            widget = self.widgets[lang]
            self.updateWidget(widget, lang)
            widget.update()
        default_value = self.default_value()
        if default_value is not None:
            lang = storage.KEY_DEFAULT
            widget = widgets[lang] = self.default_widget(self.request)
            self.initWidget(widget, lang)
            widget = self.widgets[lang]
            self.updateWidget(widget, lang)
            widget.update()

    def initWidget(self, widget, language):
        widget.id = str('{0}.{1}'.format(self.name, language))
        widget.form = self.form
        widget.mode = self.mode
        widget.ignoreContext = self.ignoreContext
        widget.ignoreRequest = self.ignoreRequest
        widget.field = self.field.value_type
        widget.name = str('{0}.i18n.{1}'.format(self.name, language))
        widget.label = self.label
        widget.lang = language

    def extract(self, default=NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        form_keys = self.request.form.keys()
        can_add = '{0}.button_add'.format(self.name) in form_keys
        available_languages = copy(self.sorted_languages())
        available_languages.append(storage.KEY_DEFAULT)
        result = {}

        for key in form_keys:
            if not key.startswith(self.name):
                continue
            lang = key.split('.').pop()
            if lang == 'add' and can_add:
                lang = self.request.get(key, default)
                if isinstance(lang, list):
                    lang = lang.pop()
                if lang in available_languages:
                    result[lang] = u''
            else:
                if lang in available_languages:
                    result[lang] = self.request.get(key, default)
        if len(result.keys()) < 1:
            result = default
        return result

    def updateWidget(self, widget, language):
        widget.value = self.getValue(language)

    def getWidget(self, language):
        return self.widgets.get(language)

    def getValue(self, language):
        self.value = removeSecurityProxy(self.value)
        if not isinstance(self.value, dict) and \
           not isinstance(self.value, PersistentDict):
            converter = IDataConverter(self)
            try:
                self.value = converter.toFieldValue(self.value)
            except Exception:
                self.value = {}
        if self.value is not None:
            return self.value.get(language)

    def hasValue(self, language):
        return bool(self.getValue(language))

    def render(self):
        return super(I18NWidget, self).render()

    @property
    def button_add_language_i18n(self):
        return translate(self.button_add_language, context=self.request)


class I18NTextWidget(I18NWidget, text.TextWidget):
    """I18N text input type implementation."""
    implementsOnly(II18NTextWidget)

    default_widget = text.TextWidget

    maxlength = I18NWidgetProperty('maxlength')
    size = I18NWidgetProperty('size')

    def updateWidget(self, widget, language):
        super(I18NTextWidget, self).updateWidget(widget, language)
        widget.maxlength = widget.field.max_length


@adapter(interfaces.II18NTextLineField, IFormLayer)
@implementer(IFieldWidget)
def I18NTextFieldWidget(field, request):
    """IFieldWidget factory for I18NTextWidget."""
    return FieldWidget(field, I18NTextWidget(request))


class I18NTextAreaWidget(I18NWidget, textarea.TextAreaWidget):
    """I18N text input type implementation."""
    implementsOnly(II18NTextAreaWidget)

    default_widget = textarea.TextAreaWidget

    rows = I18NWidgetProperty('rows')
    cols = I18NWidgetProperty('cols')
    readonly = I18NWidgetProperty('readonly')
    onselect = I18NWidgetProperty('onselect')


@adapter(interfaces.II18NTextField, IFormLayer)
@implementer(IFieldWidget)
def I18NTextAreaFieldWidget(field, request):
    """IFieldWidget factory for I18NTextWidget."""
    return FieldWidget(field, I18NTextAreaWidget(request))


@implementer(IPublishTraverse)
class WidgetAjax(BrowserView):

    def __init__(self, context, request):
        context = removeSecurityProxy(context)
        super(WidgetAjax, self).__init__(context, request)
        self.language = None

    def publishTraverse(self, request, name):
        if self.language is None:
            self.language = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        if self.language is None:
            return
        widget = self.context.getWidget(self.language)
        if widget is not None:
            return widget.render()
