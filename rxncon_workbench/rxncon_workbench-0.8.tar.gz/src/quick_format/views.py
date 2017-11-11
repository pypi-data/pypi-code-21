import os
import pickle

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .forms import QuickForm, DeleteQuickForm
from .models import Quick

try:
    from rxncon_site.views import compare_systems, create_rxncon_system_object
    from fileTree.models import File
    from rxncon_system.models import Rxncon_system
except ImportError:
    from src.rxncon_site.views import compare_systems, create_rxncon_system_object
    from src.rxncon_system.models import Rxncon_system
    from src.fileTree.models import File


def quick_detail(request, id, compare_dict=None):
    instance = Quick.objects.get(id=id)
    if instance.rxncon_system:
        pickled_rxncon_system = Rxncon_system.objects.get(project_id=id, project_type="Quick")
        rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)
    else:
        rxncon_system = None

    context_data = {
        "title": instance.name,
        "instance": instance,
        "loaded": instance.loaded,
    }

    if rxncon_system:
        context_data["nr_reactions"] = len(rxncon_system.reactions)
        context_data["nr_contingencies"] = len(rxncon_system.contingencies)

    if compare_dict:
        context_data.update(compare_dict)

    return render(request, "quick_detail.html", context_data)


def quick_compare(request, id):
    loaded = File.objects.filter(loaded=True)
    if not loaded:
        # Quick
        loaded = Quick.objects.filter(loaded=True)
        pickled_rxncon_system = Rxncon_system.objects.get(project_id=loaded[0].id, project_type="Quick")
    else:
        # File
        pickled_rxncon_system = Rxncon_system.objects.get(project_id=loaded[0].id, project_type="File")

    loaded_rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)
    differences = compare_systems(request, id, loaded_rxncon_system, called_from="Quick")

    compare_dict = {
        "compare_nr_reactions": len(loaded_rxncon_system.reactions),
        "compare_nr_contingencies": len(loaded_rxncon_system.contingencies),
        "nr_different_reactions": differences["rxns"],
        "nr_different_contingencies": differences["cnts"],
    }

    return quick_detail(request, id, compare_dict)


def quick_new(request):
    form = QuickForm(request.POST or None, request.FILES or None)
    media_url = settings.MEDIA_URL
    media_root = settings.MEDIA_ROOT

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()

        filename = instance.slug + "_quick_definition.txt"
        model_path = "%s/%s/%s/%s" % (media_root, instance.slug, "description", filename)

        try:
            os.mkdir("%s/%s" % (media_root, instance.slug))
            os.mkdir("%s/%s/%s" % (media_root, instance.slug, "description"))
            with open(model_path, mode='w') as f:
                f.write(instance.quick_input)
        except FileExistsError as e:
            context = {
                "project_name": instance.name,
                "error": "There already is a project with the name \"" + str(
                    instance.name) + "\". Please choose another name."
            }
            instance.delete()
            return render(request, 'error.html', context)

        return HttpResponseRedirect(instance.load())

    context = {
        "form": form,
    }
    return render(request, "quick_form.html", context)


def quick_delete(request, id):
    q = get_object_or_404(Quick, id=id)
    if request.method == 'POST':
        form = DeleteQuickForm(request.POST, instance=q)
        if form.is_valid():  # checks CSRF
            if q.rxncon_system:
                q.rxncon_system.delete()
            if q.reg_graph:
                q.reg_graph.delete()
            if q.rea_graph:
                q.rea_graph.delete()
            if q.sRea_graph:
                q.sRea_graph.delete()
            if q.boolean_model:
                q.boolean_model.delete()
            if q.rule_based_model:
                q.rule_based_model.delete()
            q.delete_from_harddisk()
            q.delete()
            messages.success(request, "Successfully deleted")
            return HttpResponseRedirect("/")  # wherever to go after deleting
    else:
        form = DeleteQuickForm(instance=q)
    template_vars = {'form': form,
                     'name': q.name,
                     'timestamp': q.timestamp,
                     'quick_input': q.quick_input,
                     "download": q.get_download_url()
                     }
    return render(request, 'quick_delete.html', template_vars)


def quick_update(request, id=None):
    instance = get_object_or_404(Quick, id=id)
    form = QuickForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Item Saved", extra_tags='html_safe')
        return quick_load(request, id, update=True)
    context_data = {
        "title": instance.name,
        "instance": instance,
        "form": form,
    }
    return render(request, "quick_form.html", context_data)


def quick_load(request, id, update=False):
    File.objects.all().update(loaded=False)
    Quick.objects.all().update(loaded=False)
    target = Quick.objects.get(id=id)
    if not target.rxncon_system:
        try:
            rxncon_system = create_rxncon_system_object(request=request, project_name=target.name,
                                                        project_type="Quick", project_id=id)
        except SyntaxError as e:
            context = {
                "project_name": target.name,
                "error": e,
                "sender": target,
                "sender_type": "Quick",
            }
            return render(request, 'error.html', context)
    elif update:
        target.rxncon_system.delete()
        rxncon_system = create_rxncon_system_object(request=request, project_name=Quick.objects.get(id=id).name,
                                                    project_type="Quick", project_id=id)

    else:
        rxncon_system = Quick.objects.get(id=id).rxncon_system

    target = Quick.objects.filter(
        id=id)  # target has to be redone with filter function, to make following update steps work
    target.update(loaded=True)
    target.update(rxncon_system=rxncon_system)
    if target[0].loaded:
        messages.info(request, "Quick definition '" + target[0].name + "' successfully loaded")
    return quick_detail(request, id)
