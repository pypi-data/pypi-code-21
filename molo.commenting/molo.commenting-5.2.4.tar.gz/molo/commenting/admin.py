# -*- coding: utf-8 -*-
import sys
from django_comments.models import CommentFlag
from django_comments.admin import CommentsAdmin
from django.contrib import admin
from django.contrib.admin.templatetags.admin_static import static
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.conf.urls import patterns, url
from django.contrib.admin.views.main import ChangeList
from django.shortcuts import get_object_or_404
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from molo.commenting.admin_views import MoloCommentsAdminView
from mptt.admin import MPTTModelAdmin

from molo.commenting.models import MoloComment, CannedResponse
from molo.commenting.views import AdminCommentReplyView
from molo.core.models import ArticlePage

from daterange_filter.filter import DateRangeFilter

from wagtail.contrib.modeladmin.options import ModelAdmin \
    as WagtailModelAdmin, ModelAdminGroup


class MoloCommentAdmin(MPTTModelAdmin, CommentsAdmin):
    list_display = (
        'comment', 'moderator_reply', 'content', '_user', 'is_removed',
        'is_reported', 'reported_count', 'submit_date')
    list_filter = ('submit_date', 'site', 'is_removed')
    mptt_indent_field = "comment"
    # This will ensure that MPTT can order the comments in a tree form
    ordering = ('-tree_id', "submit_date")

    def get_urls(self):
        urls = super(MoloCommentAdmin, self).get_urls()
        my_urls = patterns(
            '',
            url(
                r'(?P<parent>\d+)/reply/$',
                self.admin_site.admin_view(AdminCommentReplyView.as_view()),
                name="commenting_molocomment_reply")
        )
        return my_urls + urls

    def is_reported(self, obj):
        if (obj.flag_count(CommentFlag.SUGGEST_REMOVAL) > 0):
            return True
        return False
    is_reported.boolean = True

    def reported_count(self, obj):
        return obj.flag_count(CommentFlag.SUGGEST_REMOVAL)
    reported_count.short_description = 'Times reported'

    def moderator_reply(self, obj):
        # We only want to reply to root comments
        if obj.parent is None:
            reply_url = reverse(
                'admin:commenting_molocomment_reply', args=(obj.id,))
            image_url = static('admin/img/icon_addlink.gif')
            return '<img src="%s" alt="add" /> <a href="%s">Add reply</a>' % (
                image_url, reply_url)
        else:
            return ''
    moderator_reply.allow_tags = True

    def get_user_display_name(self, obj):
        if obj.name.lower().startswith('anon'):
            return obj.user.username
        return obj.name

    def _user(self, obj):
        if not obj.user:
            return ""

        url = '/admin/auth/user/edit/%s/' % obj.user.pk
        return '<a href="?user=%s">%s</a>' % (
            obj.user.id,
            self.get_user_display_name(obj)
        ) + ' (<a href="%s">edit</a>)' % url
    _user.allow_tags = True
    _user.short_description = 'User'

    def content(self, obj, *args, **kwargs):
        content_type = obj.content_type
        if not int(obj.object_pk) in self.ct_map[content_type]:
            content = obj
        else:
            content = self.ct_map[content_type][int(obj.object_pk)]
        url = reverse('admin:%s_%s_moderate' % (
            content_type.app_label,
            content_type.model
        ), args=(content.id,))

        return '<a href="%s">%s</a>' % (url, content)

    content.allow_tags = True
    content.short_description = 'Content'

    def flag_comments(self, request, queryset):
        super(MoloCommentAdmin, self).flag_comments(self, request, queryset)
    flag_comments.short_description = "Report selected comments"

    def get_changelist(self, request):
        class ModeratorChangeList(ChangeList):
            def get_queryset(self, request):
                """
                Used by AdminModeratorMixin.moderate_view to somewhat hackishly
                limit comments to only those for the object under review, but
                only if an obj attribute is found on request (which means the
                mixin is being applied and we are not on the standard
                changelist_view).
                """
                qs = super(ModeratorChangeList, self).get_queryset(request)
                obj = getattr(request, 'obj', None)
                if obj:
                    ct = ContentType.objects.get_for_model(obj)
                    qs = qs.filter(content_type=ct, object_pk=obj.pk)
                return qs

            def get_results(self, request):
                """
                Create a content_type map to individual objects through their
                id's to avoid additional per object queries for generic
                relation lookup (used in MoloCommentAdmin.content method).
                Also create a comment_reply map to avoid additional reply
                lookups per comment object
                (used in CommentAdmin.moderator_reply method)
                """
                super(ModeratorChangeList, self).get_results(request)
                comment_ids = []
                object_pks = []

                results = list(self.result_list)
                for obj in results:
                    comment_ids.append(obj.id)
                    object_pks.append(obj.object_pk)

                ct_map = {}
                for obj in results:
                    if obj.content_type not in ct_map:
                        ct_map.setdefault(obj.content_type, {})
                        for content_obj in obj.content_type.model_class()\
                                ._default_manager.filter(pk__in=object_pks):
                            ct_map[
                                obj.content_type][content_obj.id] = content_obj
                self.model_admin.ct_map = ct_map

        return ModeratorChangeList


class AdminModeratorMixin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Override change view to add extra context enabling moderate tool.
        """
        context = {
            'has_moderate_tool': True
        }
        if extra_context:
            context.update(extra_context)
        return super(AdminModeratorMixin, self).change_view(
            request=request,
            object_id=object_id,
            form_url=form_url,
            extra_context=context
        )

    def get_urls(self):
        """
        Add aditional moderate url.
        """
        from django.conf.urls import patterns, url
        urls = super(AdminModeratorMixin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        return patterns(
            '',
            url(r'^(.+)/moderate/$',
                self.admin_site.admin_view(self.moderate_view),
                name='%s_%s_moderate' % info),
        ) + urls

    def moderate_view(self, request, object_id, extra_context=None):
        """
        Handles moderate object tool through a somewhat hacky changelist view
        whose queryset is altered via MoloCommentAdmin.get_changelist to only
        list comments for the object under review.
        """
        opts = self.model._meta
        app_label = opts.app_label

        view = MoloCommentAdmin(model=MoloComment, admin_site=self.admin_site)

        view.list_filter = ()
        view.list_display = (
            'comment',
            'content_object',
            '_user',
            'submit_date',
        )

        model = self.model
        obj = get_object_or_404(model, pk=unquote(object_id))
        request.obj = obj
        view.change_list_template = self.change_list_template or [
            'admin/%s/%s/moderate.html' % (
                app_label, opts.object_name.lower()),
            'admin/%s/moderate.html' % app_label,
            'admin/moderate.html'
        ]
        orig_has_change_permission = self.has_change_permission(request, obj)
        if not orig_has_change_permission:
            raise PermissionDenied
        extra_context = {
            'opts': opts,
            'original': obj,
            'orig_has_change_permission': orig_has_change_permission,
        }
        return view.changelist_view(request, extra_context)


class ModeratedPageAdmin(AdminModeratorMixin, admin.ModelAdmin):
    pass


class CannedResponseModelAdmin(AdminModeratorMixin, admin.ModelAdmin):
    readonly_fields = ['date_added']

    list_display = ('response_header', 'response', 'date_added')


admin.site.register(MoloComment, MoloCommentAdmin)
admin.site.register(CommentFlag)
admin.site.register(ArticlePage, ModeratedPageAdmin)
admin.site.register(CannedResponse, CannedResponseModelAdmin)


# Below here is for Wagtail Admin
class MoloCommentsDateRangeFilter(DateRangeFilter):
    template = 'admin/molo_comments_date_range_filter.html'


class MoloCommentsModelAdmin(WagtailModelAdmin, MoloCommentAdmin):
    model = MoloComment
    menu_label = 'Comments'
    menu_icon = 'edit'
    menu_order = 100
    index_view_class = MoloCommentsAdminView
    add_to_settings_menu = False
    list_display = (
        'comment', 'parent_comment', 'moderator_reply', 'content',
        '_user', 'is_removed', 'is_reported', 'reported_count',
        'submit_date',)

    list_filter = (('submit_date', MoloCommentsDateRangeFilter), 'site',
                   'is_removed',)

    search_fields = ('comment',)

    def content(self, obj, *args, **kwargs):
        if obj.content_object and obj.parent is None:
            return '<a href="{0}" target="_blank">{1}</a> ' \
                   '(<a href="/admin/pages/{2}/edit/">edit</a>)'\
                .format(obj.content_object.url,
                        obj.content_object.title.encode('utf-8'),
                        obj.content_object.pk)

        return

    content.allow_tags = True
    content.short_description = 'Content'

    def moderator_reply(self, obj):
        if obj.parent is None:
            reply_url = reverse(
                'molo-comments-admin-reply', args=(obj.id,))
            return '<a href="%s">Add reply</a>' % reply_url
        else:
            return ''
    moderator_reply.allow_tags = True

    def parent_comment(self, obj):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        if obj.parent:
            return format_html(
                '<a href="{}">{}</a>',
                "?tree_id={}".format(obj.tree_id),
                obj.parent.comment,
            )
        else:
            return format_html(
                ('<a href="{}">'
                 '<img '
                 'src = "/static/admin/img/icon-yes.svg" '
                 'alt = "True" >'
                 '</a>'),
                "?tree_id={}".format(obj.tree_id),
            )
    parent_comment.allow_tags = True

    def get_queryset(self, request):
        return MoloComment.objects.filter(wagtail_site=request.site.pk)


class MoloCannedResponsesModelAdmin(WagtailModelAdmin,
                                    CannedResponseModelAdmin):
    model = CannedResponse
    menu_label = 'Canned Responses'
    menu_icon = 'openquote'
    menu_order = 200

    list_display = ('response_header', 'response', 'date_added')

    search_fields = ('response_header',)


class CommentingModelAdminGroup(ModelAdminGroup):
    menu_label = 'Commenting'
    menu_icon = 'edit'
    menu_order = 300
    items = (MoloCommentsModelAdmin, MoloCannedResponsesModelAdmin)
