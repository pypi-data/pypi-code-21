from crispy_forms.helper import FormHelper

def form_horizontal_helper(request):
    helper = FormHelper()
    helper.form_tag = False
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-4'
    helper.field_class = 'col-lg-8'
    helper.include_media = False
    return {
        'form_horizontal_helper': helper
    }
