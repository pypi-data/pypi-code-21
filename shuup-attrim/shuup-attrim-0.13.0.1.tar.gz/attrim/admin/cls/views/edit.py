from django.utils.translation import ugettext_lazy as _
from parler.forms import TranslatableModelForm

from shuup.admin.toolbar import Toolbar
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.views import CreateOrUpdateView
from shuup_utils.lang_constants import DEFAULT_LANG, LANG_CODES

from attrim.models import Class


class EditClassToolbar(Toolbar):
    """
    Rewrite the edit toolbar, because by default shuup doesn't add a delete button.
    """
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.request = view.request
        self.product = view.object
        
        self.extend(
            get_default_edit_toolbar(
                view_object=self.view,
                save_form_id='cls_form',
                delete_url='shuup_admin:attrim.delete',
            )
        )


class ClassForm(TranslatableModelForm):
    class Meta:
        model = Class
        fields = ['name', 'code', 'product_type', 'type']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._protect_type_field()

    # TODO redundant?
    def _protect_type_field(self):
        """
        Disabled editing of `type` field on an existing instance,
        otherwise a user may screw up the options
        """
        if self.is_bound:
            self.fields['type'].required = False
            self.fields['type'].widget.attrs['disabled'] = 'disabled'


class ClassEditView(CreateOrUpdateView):
    model = Class
    form_class = ClassForm
    template_name = 'attrim/admin/cls/edit.jinja'
    context_object_name = 'attribute'
    object = None # type: Class

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context['lang_codes'] = LANG_CODES
        context['default_lang'] = DEFAULT_LANG

        is_edit_form = self.object.pk is not None
        if is_edit_form:
            context['is_edit_form'] = 'true'
            context['cls_pk'] = self.object.pk
        else:
            context['is_edit_form'] = 'false'

        context['title'] = _('Edit attrim class')

        return context

    def get_toolbar(self) -> EditClassToolbar:
        return EditClassToolbar(view=self)
