from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from apollo.models import Layout, LayoutField, Form, FormField, FormFieldTemplate, FormSubmission
from apollo import signals
from apollo.lib import emails
from apollo.settings import apollo_settings
import logging
import graphene
import pdb

logger = logging.getLogger(__name__)


#####-----< LayoutField >----#####
class LayoutFieldInput(graphene.InputObjectType):
    id = graphene.Int()
    desktop_width = graphene.Float()
    desktop_height = graphene.Float()
    desktop_top_left = graphene.List(graphene.Float)
    mobile_width = graphene.Float()
    mobile_height = graphene.Float()
    mobile_top_left = graphene.List(graphene.Float)
    index = graphene.Int(required=False)


class LayoutFieldType(DjangoObjectType):
    class Meta:
        model = LayoutField


#####-----< Layout >----#####
class LayoutType(DjangoObjectType):
    class Meta:
        model = Layout


class LayoutInput(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
    blocks = graphene.List(LayoutFieldInput)


class CreateLayout(graphene.Mutation):
    class Arguments:
        layout_data = graphene.Argument(LayoutInput)

    layout = graphene.Field(lambda: LayoutType)

    @staticmethod
    def mutate(root, info, **args):
        data = args.get('layout_data')

        # layouts are unique on their name
        layout_name = data.get('name')

        layout, created = Layout.objects.update_or_create(name=layout_name)

        layout_blocks = data.get('blocks')

        for block in layout_blocks:
            LayoutField.objects.update_or_create(layout=layout, id=block.get('id'), defaults=block)

        return CreateLayout(layout=layout)


#####-----< FormFieldTemplate >----#####
class FormFieldTemplateType(DjangoObjectType):
    class Meta:
        model = FormFieldTemplate


class FormFieldTemplateInput(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
    input_type = graphene.String()
    is_visible = graphene.Boolean()
    is_submission_label = graphene.Boolean()
    label = graphene.String()
    label_position = graphene.String()
    placeholder = graphene.String()
    default_value = graphene.String()
    value_choices = graphene.List(graphene.List(graphene.String))
    validation_rule = graphene.String()


class CreateFormFieldTemplate(graphene.Mutation):
    class Arguments:
        form_field_template_data = graphene.Argument(FormFieldTemplateInput)

    form_field_template = graphene.Field(lambda: FormFieldTemplateType)

    @staticmethod
    def mutate(root, info, **args):
        data = args.get('form_field_template_data')

        # we define formfieldtemplate's by their name. So we update or create based on this name
        field_name = data.get('name')

        form_field_template, created = FormFieldTemplate.objects.update_or_create(name=field_name, defaults=data)

        return CreateFormFieldTemplate(form_field_template=form_field_template)


class DeleteFormFieldTemplate(graphene.Mutation):
    class Arguments:
        form_field_template_id = graphene.Int()

    status = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        FormFieldTemplate.objects.filter(id=args.get('form_field_template_id')).delete()
        return DeleteFormFieldTemplate(status='Field Deleted')


#####-----< FormField >----#####
class FormFieldType(DjangoObjectType):
    name = graphene.String()
    input_type = graphene.String()
    is_visible = graphene.Boolean()
    is_submission_label = graphene.Boolean()

    ## we need these special resolvers because there are certain base fields which an individual form field can't override from its template
    def resolve_name(self, info):
        return self.name

    def resolve_input_type(self, info):
        return self.input_type

    def resolve_is_visible(self, info):
        return self.is_visible

    def resolve_is_submission_label(self, info):
        return self.is_submission_label

    class Meta:
        model = FormField


class FormFieldInput(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
    input_type = graphene.String()
    is_visible = graphene.Boolean()
    is_submission_label = graphene.Boolean()
    label = graphene.String()
    label_position = graphene.String()
    placeholder = graphene.String()
    default_value = graphene.String()
    value_choices = graphene.List(graphene.List(graphene.String))
    validation_rule = graphene.String()
    index = graphene.Int()

    layout = graphene.Field(lambda: LayoutFieldInput, required=False)
    value = graphene.String(required=False)


class UpdateFormField(graphene.Mutation):
    class Arguments:
        field_id = graphene.Argument(graphene.Int)
        update_data = graphene.Argument(FormFieldInput)

    status = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        field_id = args.get('field_id')
        field_data = args.get('update_data')

        FormField.objects.filter(id=field_id).update(**dict(
            label=field_data.get('label'),
            label_position=field_data.get('label_position'),
            placeholder=field_data.get('placeholder'),
            default_value=field_data.get('default_value'),
            value_choices=field_data.get('value_choices'),
            validation_rule=field_data.get('validation_rule'),
        ))

        return UpdateFormField(status='success')


#####-----< Form >----#####
class FormType(DjangoObjectType):
    class Meta:
        model = Form


class FormInput(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
    redirect_url = graphene.String()
    success_message = graphene.String()
    submit_button_text = graphene.String()
    submission_url = graphene.String()
    submission_contacts = graphene.String()

    layout = graphene.Field(lambda: LayoutInput)
    fields = graphene.List(FormFieldInput)


class CreateForm(graphene.Mutation):
    class Arguments:
        form_data = graphene.Argument(FormInput)

    form = graphene.Field(lambda: FormType)
    status = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        data = args.get('form_data')

        layout = None

        layout_dat = data.get('layout')

        if layout_dat and layout_dat.get('name'):
            # the layout is update or create on ID
            layout, created = Layout.objects.update_or_create(id=layout_dat.get('id'), defaults=dict(
                name=layout_dat.get('name')
            ))

        # the form is update or create on name
        name = data.get('name')

        form, form_created = Form.objects.update_or_create(name=name, defaults=dict(
            redirect_url=data.get('redirect_url'),
            success_message=data.get('success_message'),
            submit_button_text=data.get('submit_button_text', 'Submit'),
            submission_url=data.get('submission_url'),
            submission_contacts=[c.strip() for c in data['submission_contacts'].split(',')] if data.get('submission_contacts') else None,
            layout=layout
        ))

        # parse the form fields
        for raw_field in data.get('fields'):
            raw_field_layout = raw_field.get('layout')

            # field layout is update or create on ID
            field_layout = None

            # if the raw field layout has a layout different from `layout`, it means the form is being edited AND its
            # layout has been swapped AND in the new layout the field wasn't assigned a layout. So, clear its layout.
            field_layout_removed = not layout or (raw_field_layout and raw_field_layout.get('id') and not layout.blocks.filter(id=raw_field_layout.get('id')).exists())

            if raw_field_layout and not field_layout_removed:
                field_layout, created = LayoutField.objects.update_or_create(id=raw_field_layout.get('id'), defaults=dict(
                    layout=layout,
                    desktop_width=raw_field_layout.get('desktop_width'),
                    desktop_height=raw_field_layout.get('desktop_height'),
                    desktop_top_left=raw_field_layout.get('desktop_top_left'),
                    mobile_width=raw_field_layout.get('mobile_width'),
                    mobile_height=raw_field_layout.get('mobile_height'),
                    mobile_top_left=raw_field_layout.get('mobile_top_left')
                ))

            # form field is update or create on name + form
            form_field, created = FormField.objects.update_or_create(template__name=raw_field['name'], form=form, defaults=dict(
                label=raw_field.get('label'),
                placeholder=raw_field.get('placeholder'),
                default_value=raw_field.get('default_value'),
                validation_rule=raw_field.get('validation_rule'),
                value_choices=raw_field.get('value_choices'),
                template=FormFieldTemplate.objects.get(name=raw_field['name']),
                layout=field_layout,
                index=raw_field.get('index')
            ))

            logger.debug("%s field %s" % ('created' if created else 'updated', form_field))

        # if the form wasn't created, check if any fields were removed
        if not form_created:
            old_field_names = set(form.fields.values_list('template__name', flat=True))
            new_field_names = {f['name'] for f in data.get('fields')}

            to_delete = FormField.objects.filter(template__name__in=old_field_names.difference(new_field_names), form=form)

            logger.debug('about to delete %s form fields' % to_delete.count())

            to_delete.delete()

        return CreateForm(form=form, status='success')


class CloneForm(graphene.Mutation):
    class Arguments:
        form_id = graphene.Int()

    new_form = graphene.Field(lambda: FormType)
    status = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        form_id = args.get('form_id')

        form = Form.objects.get(id=form_id)
        form_copy = form.clone()

        return CloneForm(new_form=form_copy, status='success')


class DeleteForm(graphene.Mutation):
    class Arguments:
        form_id = graphene.Int()

    status = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        Form.objects.filter(id=args.get('form_id')).delete()
        return DeleteForm(status='Form Deleted')


#####-----< Form Submissions >----#####
class FormSubmissionType(DjangoObjectType):
    label = graphene.String()

    def resolve_label(self, info):
        return self.label

    class Meta:
        model = FormSubmission


class FormSubmissionInput(graphene.InputObjectType):
    fields = graphene.List(FormFieldInput)


class CreateFormSubmission(graphene.Mutation):
    class Arguments:
        form_id = graphene.Int()
        submission_data = graphene.Argument(FormSubmissionInput)

    status = graphene.String()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        try:
            form = Form.objects.get(id=args.get('form_id'))
        except ObjectDoesNotExist:
            return CreateFormSubmission(status='error', message='form with id %s does not exist' % args.get('form_id'))

        signals.form_submitted.send(
            sender=CreateFormSubmission,
            form_id=args.get('form_id'),
            raw_data=args.get('submission_data')
        )

        submission = FormSubmission(raw_data=args.get('submission_data'), form=form)
        error_msg = False

        try:
            submission.clean_data()
        except ValueError as exc:
            error_msg = 'got error cleaning submission data'
        except ValidationError as exc:
            error_msg = 'got error validating submission data'
        finally:
            submission.save()

        if error_msg:
            signals.form_submission_error.send(
                sender=CreateFormSubmission,
                form_id=submission.form_id,
                raw_data=submission.raw_data,
                error=error_msg
            )
            return CreateFormSubmission(status='error', message=error_msg)

        if form.submission_contacts and apollo_settings.SUBMISSION_EMAIL_FROM:
            emails.send(
                from_email=apollo_settings.SUBMISSION_EMAIL_FROM,
                to_emails=form.submission_contacts,
                subject='Apollo: New Form Submission',
                content='new form submission, data = %s' % str(submission.cleaned_data)
            )

        signals.form_submission_cleaned.send(
            sender=CreateFormSubmission,
            form_id=submission.form_id,
            submission_id=submission.id,
            cleaned_data=submission.cleaned_data
        )

        return CreateFormSubmission(status='success', message='submitted form successfully')


#####-----< Query >----#####
class Query(object):
    ## Static Choices
    form_field_widget_choices = graphene.List(graphene.String)
    form_field_validation_rule_choices = graphene.List(graphene.String)
    form_field_label_position_choices = graphene.List(graphene.String)

    ## Form Field Templates
    all_form_field_templates = graphene.List(FormFieldTemplateType)
    form_field_template = graphene.Field(FormFieldTemplateType,
                                         id=graphene.Int())

    ## Layouts
    all_layouts = graphene.List(LayoutType)

    ## Form Fields
    form_field = graphene.Field(FormFieldType,
                                id=graphene.Int())

    ## Forms
    all_forms = graphene.List(FormType)
    form = graphene.Field(FormType,
                          id=graphene.Int())

    ## Form Submission
    all_form_submissions = graphene.List(FormSubmissionType,
                                         form_id=graphene.Int())
    form_submission = graphene.Field(FormSubmissionType,
                                     id=graphene.Int())

    def resolve_form_field_widget_choices(self, info):
        return [_[0].upper() for _ in FormFieldTemplate.FIELD_TYPES]

    def resolve_form_field_validation_rule_choices(self, info):
        return [_[0].upper() for _ in FormFieldTemplate.VALIDATION_RULES]

    def resolve_form_field_label_position_choices(self, info):
        return [_[0].upper() for _ in FormFieldTemplate.LABEL_POSITIONS]

    def resolve_all_form_field_templates(self, info):
        return FormFieldTemplate.objects.all()

    def resolve_form_field_template(self, info, **kwargs):
        id = kwargs.get('id')

        return FormFieldTemplate.objects.get(id=id)

    def resolve_all_layouts(self, info):
        return Layout.objects.all()

    def resolve_form_field(self, info, **kwargs):
        id = kwargs.get('id')

        return FormField.objects.get(id=id)

    def resolve_all_forms(self, info):
        return Form.objects.all()

    def resolve_form(self, info, **kwargs):
        id = kwargs.get('id')

        return Form.objects.get(id=id)

    def resolve_all_form_submissions(self, info, **kwargs):
        return FormSubmission.objects.filter(form_id=kwargs.get('form_id')).select_related('form').all()

    def resolve_form_submission(self, info, **kwargs):
        id = kwargs.get('id')

        return FormSubmission.objects.get(id=id)


class Mutations(object):
    ## Form Field Templates
    create_form_field_template = CreateFormFieldTemplate.Field()
    delete_form_field_template = DeleteFormFieldTemplate.Field()

    ## Layouts
    create_layout = CreateLayout.Field()

    ## Form Fields
    update_form_field = UpdateFormField.Field()

    # Forms
    create_form = CreateForm.Field()
    clone_form = CloneForm.Field()
    delete_form = DeleteForm.Field()

    # Form Submission
    create_form_submission = CreateFormSubmission.Field()


class APIQuery(Query, graphene.ObjectType):
    pass


class APIMutation(Mutations, graphene.ObjectType):
    pass


api_schema = graphene.Schema(query=APIQuery, mutation=APIMutation)