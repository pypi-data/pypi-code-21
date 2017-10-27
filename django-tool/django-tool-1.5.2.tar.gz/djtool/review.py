from django.views.generic import View, TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import MultipleObjectMixin
from djtool.dss.Serializer import serializer
from django.http import JsonResponse
from djtool.common import Common
from django.shortcuts import get_object_or_404
import importlib
from django.core.cache import cache
import urllib


class MultipleObjectMixin(MultipleObjectMixin):

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs


class View(View, Common):

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        if hasattr(self, 'patch'):
            patch = self.import_model(self.patch)
            request, args, kwargs = patch(request, args, kwargs)
        return handler(request, *args, **kwargs)


class TemplateView(TemplateView, View):

    def get(self, request, *args, **kwargs):
        if hasattr(self, 'content') and isinstance(self.content, dict):
            for key, value in self.content.items():
                kwargs[key] = value
        kwargs["l"] = "{{"
        kwargs["r"] = "}}"
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class ListView(TemplateResponseMixin, MultipleObjectMixin, View):

    def __get_result(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        paginator = self.paginator if hasattr(self, 'paginator') else True
        if paginator:
            if hasattr(self, 'pre'):
                pre = self.pre
            elif request.GET.get('limit'):
                pre = self.request.GET.get('limit')
            else:
                pre = 10
            page = Common.page(self.object_list, request.GET.get('curr'), pre=pre)
            self.object_list = page
        fomat = self.serializer if hasattr(self, 'serializer') else {}
        data = serializer(self.object_list, **fomat)
        if paginator:
            d = []
            i = 0
            uuids = []
            for row in data:
                if self.show_id:
                    i += 1
                    row['id'] = Common.ID_desc(page.paginator.count, request.GET.get('curr'), i)
                d.append(row)
                uuids.append(row['uuid'])
            result = {"data": d, "total": page.paginator.num_pages, "count": page.paginator.count}
        else:
            result = {"data": data, "count": len(data)}
        return result

    def get(self, request, *args, **kwargs):
        if request.GET.get('curr'):
            if hasattr(self, 'cache') and self.cache:
                key = request.get_full_path()
                result = cache.get(key)
                if not result:
                    result = self.__get_result(request, *args, **kwargs)
                    cache.set(key, result, timeout=60 * 60)
            else:
                result = self.__get_result(request, *args, **kwargs)
            return JsonResponse(result)
        elif request.GET.get('page'):
            if hasattr(self, 'cache') and self.cache:
                key = request.get_full_path()
                result = cache.get(key)
                if not result:
                    result = self.__get_result(request, *args, **kwargs)
                    cache.set(key, result, timeout=60 * 60)
            else:
                result = self.__get_result(request, *args, **kwargs)
            layui_table = {}
            layui_table['code'] = 0
            layui_table['msg'] = ""
            layui_table['count'] = result["count"]
            layui_table['data'] = result["data"]
            return JsonResponse(layui_table)
        else:
            if request.GET.get('uuid') and hasattr(self, 'model_class') and self.model_class:
                content_name = str(self.model_class._meta).split('.')[-1]
                kwargs[content_name] = get_object_or_404(self.model_class, uuid=request.GET.get('uuid'))
            if hasattr(self, 'content') and isinstance(self.content, dict):
                for key, value in self.content.items():
                    kwargs[key] = value
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        if request.GET.get('uuid'):
            if hasattr(self, 'relation') and self.relation:
                query_delete = self.queryset.filter(uuid__in=request.GET.get('uuid', '').split(','))
                print(query_delete)
                print(self.relation)
                print(isinstance(self.relation, str))
                if isinstance(self.relation, str):
                    getattr(get_object_or_404(self.model_class, uuid=request.GET.get('id')), self.relation).remove(*query_delete)
                else:
                    getattr(get_object_or_404(self.model_class, uuid=request.GET.get('id')), str(query_delete.model._meta).split('.')[-1]).remove(*query_delete)
            else:
                self.queryset.filter(uuid__in=request.GET.get('uuid', '').split(',')).update(del_state=0)
            return JsonResponse(self.msg(1, '1006'))
        return JsonResponse(self.msg(0, '4000'))


class ActionView(TemplateView, Common):

    def get(self, request, *args, **kwargs):
        if request.GET.get('uuid') and hasattr(self, 'model_class') and self.model_class:
            content_name = self.__class__.__name__.lower().replace('view', '')
            kwargs[content_name] = get_object_or_404(self.model_class, uuid=request.GET.get('uuid'), del_state=1)
            kwargs['action'] = 'edit'
        else:
            kwargs['action'] = 'add'
        if hasattr(self, 'content') and isinstance(self.content, dict):
            for key, value in self.content.items():
                kwargs[key] = value
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        data = request.data if hasattr(request, 'data') else request.POST
        form = self.form_class(data)
        if form.is_valid():
            if hasattr(self, 'method_post') and len(self.method_post) == 2:
                method = self.method_post[0].split('.')
                method_class = '.'.join(method[:-1])
                action_class = getattr(importlib.import_module(method_class), method[-1])
                class_object = action_class(admin=request.admin)
                result = getattr(class_object, self.method_post[1])(**form.cleaned_data)
            else:
                form.save()
                result = self.msg(1, '1002')
            return JsonResponse(result)
        return JsonResponse(self.msg(0, form.error_text(), type=True))

    def put(self, request, *args, **kwargs):
        if request.GET.get('uuid') and hasattr(self, 'model_class') and self.model_class:
            request.data = dict(urllib.parse.parse_qsl(request.body.decode()))
            try:
                object_one = self.model_class.objects.get(uuid=request.GET.get('uuid'), del_state=1)
                form = self.form_class(request.data.copy(), instance=object_one)
                if form.is_valid():
                    if hasattr(self, 'method_put') and len(self.method_put) == 2:
                        method = self.method_put[0].split('.')
                        method_class = '.'.join(method[:-1])
                        action_class = getattr(importlib.import_module(method_class), method[-1])
                        class_object = action_class()
                        result = getattr(class_object, self.method_put[1])(request, form, *args, **kwargs)
                    else:
                        form.save()
                        result = self.msg(1, '1004')
                        return JsonResponse(result)
            except:
                return JsonResponse(self.msg(0, '4000'))
        return JsonResponse(self.msg(0, form.error_text(), type=True))
