try:
    from rxncon_site.views import compare_systems, create_rxncon_system_object
    from quick_format.models import Quick
    from rxncon_system.models import Rxncon_system

except ImportError:
    from src.rxncon_site.views import compare_systems, create_rxncon_system_object
    from src.quick_format.models import Quick
    from src.rxncon_system.models import Rxncon_system

import pickle

import django.forms as forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .forms import DeleteFileForm, FileForm
from .models import File


def file_detail(request, id, compare_dict=None):
    instance = File.objects.get(id=id)
    slug = File.objects.filter(id=id).values("slug")
    project_files = File.objects.filter(slug=slug).order_by("-updated")
    if instance.rxncon_system:
        pickled_rxncon_system = Rxncon_system.objects.get(project_id=id, project_type="File")
        rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)
    else:
        rxncon_system = None

    context_data = {
        "project_files": project_files,
        "title": instance.project_name,
        "instance": instance,
        "loaded": instance.loaded,
    }

    if rxncon_system:
        context_data["nr_reactions"] = len(rxncon_system.reactions)
        context_data["nr_contingencies"] = len(rxncon_system.contingencies)

    if compare_dict:
        context_data.update(compare_dict)

    return render(request, "file_detail.html", context_data)


def file_compare(request, id):
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

    return file_detail(request, id, compare_dict)


def file_upload(request, slug=None):
    form = FileForm(request.POST or None, request.FILES or None)
    context = {}
    if slug != None:  # add file to existing project
        try:
            file = File.objects.filter(slug=slug)[0]
            project_name = file.project_name
            form = FileForm(request.POST or None, request.FILES or None, initial={'project_name': project_name})
            form.fields['project_name'].widget = forms.HiddenInput()

            context.update({
                'add_to_project': True,
                'project_name': project_name,
            })

        except KeyError:
            pass

    if form.is_valid():
        print("Valid form")
        instance = form.save(commit=False)
        instance.save()
        # return HttpResponseRedirect(instance.get_absolute_url())
        return HttpResponseRedirect(instance.load())

    context.update({
        "form": form,
    })
    return render(request, "file_form.html", context)


def file_delete(request, pk):
    f = get_object_or_404(File, pk=pk)
    project_name = f.project_name
    timestamp = f.timestamp
    filename = f.get_filename()
    download = f.get_download_url()
    if request.method == 'POST':
        form = DeleteFileForm(request.POST, instance=f)
        if form.is_valid():  # checks CSRF
            if f.rxncon_system:
                f.rxncon_system.delete()
            if f.reg_graph:
                f.reg_graph.delete()
            if f.rea_graph:
                f.rea_graph.delete()
            if f.sRea_graph:
                f.sRea_graph.delete()
            if f.boolean_model:
                f.boolean_model.delete()
            if f.rule_based_model:
                f.rule_based_model.delete()

            f.delete_file_from_harddisk()
            f.delete()
            messages.success(request, "Successfully deleted")
            try:
                other_file_id = str(File.objects.filter(project_name=project_name).latest("updated").id)
                if other_file_id:
                    return HttpResponseRedirect("/files/" + other_file_id + "/")  # wherever to go after deleting
            except:
                return HttpResponseRedirect("/")


    else:
        form = DeleteFileForm(instance=f)

    template_vars = {'form': form,
                     'project_name': project_name,
                     "timestamp": timestamp,
                     "file": filename,
                     "download": download,
                     }
    return render(request, 'file_delete.html', template_vars)


def file_delete_project(request, slug):
    project = File.objects.filter(slug=slug).order_by("-updated")
    f = project[0]  # latest file
    project_name = f.project_name
    timestamp = f.timestamp
    if request.method == 'POST':
        form = DeleteFileForm(request.POST, instance=f)
        if form.is_valid():  # checks CSRF
            if f.rxncon_system:
                f.rxncon_system.delete()
            if f.reg_graph:
                f.reg_graph.delete()
            if f.rea_graph:
                f.rea_graph.delete()
            if f.sRea_graph:
                f.sRea_graph.delete()
            if f.boolean_model:
                f.boolean_model.delete()
            if f.rule_based_model:
                f.rule_based_model.delete()
            f.delete_project_from_harddisk()
            project.delete()
            messages.success(request, "Successfully deleted")
            return HttpResponseRedirect("/")  # wherever to go after deleting
    else:
        form = DeleteFileForm(instance=f)
    template_vars = {'form': form,
                     'project': project_name,
                     "timestamp": timestamp,
                     "download": f.get_download_url(),
                     }
    return render(request, 'file_delete.html', template_vars)


def file_load(request, id):
    File.objects.all().update(loaded=False)
    Quick.objects.all().update(loaded=False)
    target = File.objects.get(id=id)
    if not target.rxncon_system:
        try:
            rxncon_system = create_rxncon_system_object(request=request, project_name=target.project_name,
                                                        project_type="File", project_id=id)
        except SyntaxError as e:

            context = {
                "project_name": target.project_name,
                "file_name": target.get_filename(),
                "error": e,
                "sender": target,
                "sender_type": "File",
            }
            return render(request, 'error.html', context)
    else:
        rxncon_system = File.objects.get(id=id).rxncon_system

    target = File.objects.filter(
        id=id)  # target has to be redone with filter function, to make following update steps work
    target.update(loaded=True)
    target.update(rxncon_system=rxncon_system)
    if target[0].loaded:
        messages.info(request, "File '" + target[0].get_filename() + "' successfully loaded")
    return file_detail(request, id)
