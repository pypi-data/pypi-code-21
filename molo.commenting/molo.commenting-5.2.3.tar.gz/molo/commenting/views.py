from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import FormView, TemplateView

import django_comments
from django_comments.views.moderation import perform_flag
from django_comments.views.comments import post_comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from molo.core.models import ArticlePage
from molo.commenting.forms import AdminMoloCommentReplyForm, MoloCommentForm
from molo.commenting.models import MoloComment


@login_required
def report(request, comment_id):
    """
    Flags a comment on GET.

    Redirects to whatever is provided in request.REQUEST['next'].
    """

    comment = get_object_or_404(
        django_comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)
    if comment.parent is not None:
        messages.info(request, _('Reporting comment replies is not allowed.'))
    else:
        perform_flag(request, comment)
        messages.info(request, _('The comment has been reported.'))

    next = request.GET.get('next') or comment.get_absolute_url()
    return HttpResponseRedirect(next)


@login_required
def post_molo_comment(request, next=None, using=None):
    """
    Allows for posting of a Molo Comment, this allows comments to
    be set with the "user_name" as "Anonymous"
    """
    data = request.POST.copy()
    if 'submit_anonymously' in data:
        data['name'] = _('Anonymous')
    # replace with our changed POST data

    # ensure we always set an email
    data['email'] = request.user.email or 'blank@email.com'

    request.POST = data
    return post_comment(request, next=next, using=next)


def view_more_article_comments(request, page_id):
    article = get_object_or_404(ArticlePage, id=page_id)
    qs = MoloComment.objects.for_model(ArticlePage).filter(
        object_pk=page_id, parent__isnull=True)

    try:
        comments_per_page = settings.COMMENTS_PER_PAGE
    except AttributeError:
        comments_per_page = 20

    paginator = Paginator(qs, comments_per_page)
    page = request.GET.get('p', 1)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    return render(
        request, 'comments/comments.html', {
            "self": article,
            "page": comments,
            "comments": [
                c.get_descendants(include_self=True) for c in comments],
        })


def report_response(request, comment_pk):
    comment = MoloComment.objects.get(pk=comment_pk)

    return render(request, 'comments/report_response.html', {
        'article': comment.content_object,
    })


class AdminCommentReplyView(FormView):
    form_class = AdminMoloCommentReplyForm
    template_name = 'admin/reply.html'
    success_url = reverse_lazy('admin:commenting_molocomment_changelist')

    def get_form_kwargs(self):
        kwargs = super(AdminCommentReplyView, self).get_form_kwargs()
        kwargs['parent'] = self.kwargs['parent']
        return kwargs

    def form_valid(self, form):
        self.request.POST = self.request.POST.copy()
        self.request.POST['name'] = ''
        self.request.POST['url'] = ''
        self.request.POST['email'] = ''
        self.request.POST['parent'] = self.kwargs['parent']
        reply = post_comment(self.request, next=self.success_url)
        messages.success(self.request, _('Reply successfully created.'))
        return reply


class CommentReplyView(TemplateView):
    form_class = MoloCommentForm
    template_name = 'comments/reply.html'

    def get(self, request, parent_comment_pk):
        comment = get_object_or_404(
            django_comments.get_model(), pk=parent_comment_pk,
            site__pk=settings.SITE_ID)
        form = MoloCommentForm(comment.content_object, initial={
            'content_type': '%s.%s' % (
                comment.content_type.app_label,
                comment.content_type.model),
            'object_pk': comment.object_pk,
        })

        queryset = comment.get_children().reverse()

        try:
            comments_per_page = settings.COMMENTS_PER_PAGE
        except AttributeError:
            comments_per_page = 5

        paginator = Paginator(queryset, comments_per_page)
        page = request.GET.get('p', 1)
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
            page = 1
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        return self.render_to_response({
            'form': form,
            'comment': comment,
            'replies': comments,
            'page': page
        })


@login_required
def reply_list(request):
    unread_notifications = list(request.user.notifications.unread())
    read_notifications = list(request.user.notifications.read())

    for notification in unread_notifications:
        notification.unread = False
        notification.save()

    number_unread_notifications = len(unread_notifications)

    return render(request, 'notifications/reply_list.html', {
        'read_notifications': read_notifications,
        'unread_notifications': unread_notifications,
        'number_unread_notifications': number_unread_notifications,
    })
