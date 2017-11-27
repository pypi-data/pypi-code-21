# from jcms.models import Article
# from django.views.generic.detail import DetailView
# from django.views.generic.edit import CreateView
# from django.views.generic.list import ListView
# from django.views.generic.edit import UpdateView
# from django.views.generic.edit import DeleteView
# from django.core.urlresolvers import reverse_lazy
#
#
# class ArticleMixin(JcmsMixin, object):
#     model = Article
#
#
# class List(ArticleMixin, ListView):
#     template_name = 'models/articles/list.html'
#     permission_required = "jcms.create_article"
#
#
# class Detail(ArticleMixin, DetailView):
#     template_name = 'jcms-admin/crud/detail.html'
#     permission_required = "jcms.create_article"
#
#
# class Create(ArticleMixin, CreateView):
#     fields = ['code', 'title', 'content']
#     template_name = 'jcms-admin/crud/edit_or_create.html'
#     success_url = reverse_lazy('jcms:articleList')
#     permission_required = "jcms.create_article"
#
#
# class Delete(ArticleMixin, DeleteView):
#     permission_required = 'jcms.delete_article'
#     success_url = reverse_lazy('jcms:articleList')
#
#
# class Edit(ArticleMixin, UpdateView):
#     fields = ['code', 'title', 'content']
#     template_name = 'jcms-admin/crud/edit_or_create.html'
#     permission_required = 'jcms.change_article'

from jcms.mixins.jcms_crud import JcmsCrud
from jcms.models import Article


class ArticleViews(JcmsCrud):
    model = Article
    create_edit_list = ['code', 'title', 'content']
    list_fields = ['code', 'title']
