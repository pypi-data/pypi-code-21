from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView
from django_comments.views.comments import post_comment
from molo.commenting.forms import AdminMoloCommentReplyForm
from tasks import send_export_email
from wagtail.contrib.modeladmin.views import IndexView


class MoloCommentsAdminView(IndexView):
    def send_export_email_to_celery(self, email, arguments):
        send_export_email.delay(email, arguments)

    def post(self, request, *args, **kwargs):
        if not request.user.email:
            messages.error(
                request, (
                    "Your email address is not configured. "
                    "Please update it before exporting."))
            return redirect(request.path)

        drf__submit_date__gte = request.GET.get('drf__submit_date__gte')
        drf__submit_date__lte = request.GET.get('drf__submit_date__lte')
        is_removed__exact = request.GET.get('is_removed__exact')

        filter_list = {
            'submit_date__range': (drf__submit_date__gte,
                                   drf__submit_date__lte) if
            drf__submit_date__gte and drf__submit_date__lte else None,
            'is_removed': is_removed__exact
        }

        arguments = {'wagtail_site': request.site.pk}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value

        self.send_export_email_to_celery(request.user.email, arguments)
        messages.success(request, (
            "CSV emailed to '{0}'").format(request.user.email))
        return redirect(request.path)

    def get_template_names(self):
        return 'admin/molo_comments_admin.html'


class MoloCommentsAdminReplyView(FormView):
    form_class = AdminMoloCommentReplyForm
    template_name = 'admin/molo_comments_admin_reply.html'

    def get_form_kwargs(self):
        kwargs = super(MoloCommentsAdminReplyView, self).get_form_kwargs()
        kwargs['parent'] = self.kwargs['parent']
        return kwargs

    def form_valid(self, form):
        self.request.POST = self.request.POST.copy()
        self.request.POST['name'] = ''
        self.request.POST['url'] = ''
        self.request.POST['email'] = ''
        self.request.POST['parent'] = self.kwargs['parent']
        post_comment(self.request)
        messages.success(self.request, ('Reply successfully created.'))

        return redirect('/admin/commenting/molocomment/')
