from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from laporem_field.models import LaporemImage
from django.views.decorators.csrf import csrf_exempt


@login_required
def upload_files(request):
    if request.is_ajax() and request.POST:
        data={}
        base_model = request.POST.get('base_model', None)
        if base_model:
            base_model = ContentType.objects.get(model=base_model)
            for key, files in dict(request.FILES).items():
                iFiles = key.split('--')
                if len(iFiles) == 4:
                    field, value, laporem_model, any = iFiles
                    if any == 'laporem':
                        new_objs = []
                        for file in files:
                            weight = 0
                            content_type = ContentType.objects.get(model=laporem_model)
                            model = content_type.model_class()
                            objs = model.objects.filter(object_id=value, content_type=base_model, unique=field).order_by("-weight")[:1]
                            if objs:
                                weight=objs.get().weight
                            new_model = model(
                                file=file,
                                content_type=base_model,
                                object_id=value,
                                unique=field,
                                weight=weight
                            )
                            new_model.save()
                            new_objs.append(new_model)
                        data.update({'objs': new_objs, 'laporem_model_file':laporem_model})
        return render(request, 'laporem/images.html', data)

    return HttpResponse(status=400)


@login_required
def delete_obj(request, classname, id):
    content_type = ContentType.objects.get(model=classname)
    model = content_type.model_class()
    obj = get_object_or_404(model, id=id)
    obj.delete()
    return HttpResponse(status=200)


@csrf_exempt
@login_required
def delete_select(request):
    classname = request.POST.get('classname', None)
    ids = request.POST.getlist('ids[]', None)
    content_type = ContentType.objects.get(model=classname)
    model = content_type.model_class()
    model.objects.filter(id__in=ids).delete()
    return HttpResponse(status=200)


def GetLaporemObjects(obj):
    for field in obj._meta.fields:
        if field.get_internal_type() == 'LaporemImageField':
            objs = field.laporem_model_file.objects.filter(object_id=getattr(obj, field.name)).order_by('weight')
            setattr(obj, field.name, objs)
    return obj


def move(request):
    data = request.GET.getlist('list[]',None)
    model = request.GET.get('laporem_model_file', None)
    content_type = ContentType.objects.get(model=model)
    model = content_type.model_class()
    i = 0
    for id in data:
        obj = model.objects.get(id=id)
        obj.weight = i
        obj.save()
        i += 1
    return HttpResponse(status=200)
