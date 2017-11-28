from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.edit_handlers import FieldPanel

from wagtail_personalisation.rules import AbstractBaseRule


class CommentDataRule(AbstractBaseRule):
    EQUALS = 'eq'
    CONTAINS = 'in'

    OPERATOR_CHOICES = (
        (EQUALS, _('equals')),
        (CONTAINS, _('contains')),
    )
    expected_content = models.TextField(_('expected content'),
                                        help_text=_('Content that we want to '
                                                    'match in user\'s comment '
                                                    'data.'))
    operator = models.CharField(
        _('operator'), max_length=3,
        choices=OPERATOR_CHOICES, default=CONTAINS,
        help_text=_('"Equals" operator will match only '
                    'the exact content. "Contains" '
                    'operator matches a part of a '
                    'comment.'))

    panels = [
        FieldPanel('operator'),
        FieldPanel('expected_content')
    ]

    class Meta:
        verbose_name = _('comment data rule')

    def test_user(self, request):
        # Must be logged-in to use this rule
        if not request.user.is_authenticated():
            return False

        # Construct a queryset with user comments
        comments = request.user.comment_comments

        return comments.filter(
            **{'comment__i' + (
                'exact' if self.operator == self.EQUALS
                else 'contains'): self.expected_content}).exists()

    def description(self):
        return {
            'title': _('Based on comment submissions of users'),
            'value': _('"%s"') % (
                Truncator(self.expected_content).chars(20)
            )
        }
