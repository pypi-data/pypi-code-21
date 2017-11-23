from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from django_comments.forms import CommentForm
from molo.commenting.models import MoloComment, CannedResponse

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class MoloCommentForm(CommentForm):
    email = forms.EmailField(label=_("Email address"), required=False)
    parent = forms.ModelChoiceField(
        queryset=MoloComment.objects.all(),
        required=False, widget=forms.HiddenInput)
    comment = forms.CharField(
        label=_('Comment'), widget=forms.Textarea,
        max_length=COMMENT_MAX_LENGTH)

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return MoloComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the parent field field
        data = super(MoloCommentForm, self).get_comment_create_data()
        data['parent'] = self.cleaned_data['parent']
        return data

    def get_comment_object(self):
        """
        NB: Overridden to remove dupe comment check for admins (necessary for
        canned responses)

        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError(
                "get_comment_object may only be called on valid forms")

        CommentModel = self.get_comment_model()
        new = CommentModel(**self.get_comment_create_data())

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=new.user_name)
            if not user.is_staff:
                new = self.check_for_duplicate_comment(new)
        except user_model.DoesNotExist:
            # post_molo_comment may have set the username to 'Anonymous'
            new = self.check_for_duplicate_comment(new)

        return new


class AdminMoloCommentReplyForm(MoloCommentForm):
    parent = forms.ModelChoiceField(
        queryset=MoloComment.objects.all(), widget=forms.HiddenInput,
        required=False)
    email = forms.EmailField(
        label=_("Email address"), required=False, widget=forms.HiddenInput)
    url = forms.URLField(
        label=_("URL"), required=False, widget=forms.HiddenInput)
    name = forms.CharField(
        label=_("Name"), required=False, widget=forms.HiddenInput)
    honeypot = forms.CharField(
        required=False, widget=forms.HiddenInput)

    canned_response = ModelChoiceField(queryset=CannedResponse.objects.all(),
                                       label="Or add a canned response",
                                       to_field_name="response",
                                       required=False)

    def __init__(self, *args, **kwargs):
        parent = MoloComment.objects.get(pk=kwargs.pop('parent'))
        super(AdminMoloCommentReplyForm, self).__init__(
            parent.content_object, *args, **kwargs
        )
