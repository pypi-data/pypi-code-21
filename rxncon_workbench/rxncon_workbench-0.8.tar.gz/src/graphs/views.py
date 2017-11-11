import os
import pickle

import rxncon.visualization.graphML as graphML
import rxncon.visualization.reaction_graph as reaction_graph
import rxncon.visualization.regulatory_graph as regulatory_graph
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from rxncon.visualization.graphML import map_layout2xgmml

from .forms import DeleteGraphForm
from .forms import reaGraphFileForm
from .forms import regGraphFileForm
from .models import Graph_from_File

try:
    from fileTree.models import File
    from fileTree.views import file_detail
    from quick_format.models import Quick
    from quick_format.views import quick_detail
    from rxncon_system.models import Rxncon_system

except ImportError:
    from src.fileTree.models import File
    from src.fileTree.views import file_detail
    from src.quick_format.models import Quick
    from src.quick_format.views import quick_detail
    from src.rxncon_system.models import Rxncon_system


def apply_template_layout(request, graph_file_path, graph_string):
    template_file = request.FILES.get('template')
    mapped_layout = map_layout2xgmml(graph_string, template_file, str_template=True)
    with open(graph_file_path, "w") as graph_handle:
        graph_handle.write(mapped_layout)

    return graph_string


def check_filepath(request, graph_file_path, file, media_root):
    if os.path.exists(graph_file_path):
        messages.warning(request, "Graph file already exists. Delete it first in the system's detail view.")
        return False
    elif not os.path.exists("%s/%s/%s" % (media_root, file.slug, "graphs")):
        os.makedirs("%s/%s/%s" % (media_root, file.slug, "graphs"))
        return True
    else:
        return True


def regGraph(request, system_id=None):
    form = regGraphFileForm(request.POST or None)

    if not form.is_valid() and not system_id:
        context = {
            "form": form,
        }
        return render(request, "regGraphFile_form.html", context)


def regGraphFile(request, system_id=None):
    form = regGraphFileForm(request.POST or None)

    if form.is_valid():
        media_url = settings.MEDIA_URL
        media_root = settings.MEDIA_ROOT

        system = File.objects.get(id=system_id)
        graph_file_name = system.slug + "_" + system.get_filename().split(".")[0] + "_regGraph.xgmml"
        graph_file_path = "%s/%s/%s/%s" % (media_root, system.slug, "graphs", graph_file_name)

        if not check_filepath(request, graph_file_path, system, media_root):
            return file_detail(request, system_id)

        pickled_rxncon_system = Rxncon_system.objects.get(project_id=system_id, project_type="File")
        rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)

        graph = regulatory_graph.RegulatoryGraph(rxncon_system).to_graph()
        xgmml_graph = graphML.XGMML(graph, system.slug)
        graph_file = xgmml_graph.to_file(graph_file_path)
        graph_string = xgmml_graph.to_string()

        if request.FILES.get('template'):
            graph_string = apply_template_layout(request, graph_file_path, graph_string)

        g = Graph_from_File(project_name=system.project_name, graph_file=graph_file_path, graph_string=graph_string,
                            comment=request.POST.get('comment'))
        g.save()

        File.objects.filter(id=system_id).update(reg_graph=g)
        messages.info(request, "Regulatory graph for project '" + g.project_name + "' successfully created.")
        return file_detail(request, system_id)


def regGraphQuick(request, system_id=None):
    form = regGraphFileForm(request.POST or None)

    if form.is_valid():
        media_url = settings.MEDIA_URL
        media_root = settings.MEDIA_ROOT

        system = Quick.objects.get(id=system_id)
        graph_file_name = system.slug + "_" + system.get_filename().split(".")[0] + "_regGraph.xgmml"
        graph_file_path = "%s/%s/%s/%s" % (media_root, system.slug, "graphs", graph_file_name)

        if not check_filepath(request, graph_file_path, system, media_root):
            return quick_detail(request, system_id)

        pickled_rxncon_system = Rxncon_system.objects.get(project_id=system_id, project_type="Quick")
        rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)
        graph = regulatory_graph.RegulatoryGraph(rxncon_system).to_graph()
        xgmml_graph = graphML.XGMML(graph, system.slug)
        graph_file = xgmml_graph.to_file(graph_file_path)
        graph_string = xgmml_graph.to_string()

        if request.FILES.get('template'):
            graph_string = apply_template_layout(request, graph_file_path, graph_string)

        g = Graph_from_File(project_name=system.name, graph_file=graph_file_path, graph_string=graph_string,
                            comment=request.POST.get('comment'))
        g.save()

        Quick.objects.filter(id=system_id).update(reg_graph=g)
        messages.info(request, "Regulatory graph for project '" + g.project_name + "' successfully created.")
        return quick_detail(request, system_id)


def reaGraph(request, system_id=None):
    form = reaGraphFileForm(request.POST or None)

    if not form.is_valid() and not system_id:
        context = {
            "form": form,
        }
        return render(request, "reaGraph_form.html", context)


class ReaGraph(View):
    def post(self, request, system_id=None):
        self.system_id = system_id
        self.request = request
        self.form = reaGraphFileForm(self.request.POST or None)

        if self.form.is_valid():
            media_url = settings.MEDIA_URL
            media_root = settings.MEDIA_ROOT
            system_type = None
            try:
                system = Quick.objects.filter(id=system_id)[0]
                system_type = "Quick"
                project_name = system.name
            except:
                system = File.objects.filter(id=system_id)[0]
                system_type = "File"
                project_name = system.project_name

            graph_file_name = system.slug + "_" + system.get_filename().split(".")[0] + "_reaGraph.xgmml"
            graph_file_path = "%s/%s/%s/%s" % (media_root, system.slug, "graphs", graph_file_name)

            if not check_filepath(request, graph_file_path, system, media_root):
                if system_type == "Quick":
                    return quick_detail(request, system_id)
                else:
                    return file_detail(request, system_id)

            pickled_rxncon_system = Rxncon_system.objects.get(project_id=system_id, project_type=system_type)
            rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)

            graph = reaction_graph.rxngraph_from_rxncon_system(rxncon_system).reaction_graph

            xgmml_graph = graphML.XGMML(graph, system.slug)
            graph_file = xgmml_graph.to_file(graph_file_path)
            graph_string = xgmml_graph.to_string()

            if request.FILES.get('template'):
                try:
                    graph_string = apply_template_layout(request, graph_file_path, graph_string)
                except AssertionError as e:
                    os.remove(graph_file_path)
                    context = {
                        "sender_type": "Graph",
                    }
                    if str(e).strip():
                        context["error"] = e
                    return render(request, 'error.html', context)

            g = Graph_from_File(project_name=project_name, graph_file=graph_file_path, graph_string=graph_string,
                                comment=request.POST.get('comment'))
            g.save()
            messages.info(request, "Reaction graph for project '" + g.project_name + "' successfully created.")
            if system_type == "Quick":
                Quick.objects.filter(id=system_id).update(rea_graph=g)
                return quick_detail(request, system_id)
            else:
                File.objects.filter(id=system_id).update(rea_graph=g)
                return file_detail(request, system_id)


def sReaGraph(request, system_id=None):
    form = reaGraphFileForm(request.POST or None)

    if not form.is_valid() and not system_id:
        context = {
            "form": form,
        }
        return render(request, "sReaGraph_form.html", context)


class SReaGraph(ReaGraph):
    def post(self, request, system_id=None):
        self.system_id = system_id
        self.request = request
        self.form = reaGraphFileForm(self.request.POST or None)

        if self.form.is_valid():
            media_url = settings.MEDIA_URL
            media_root = settings.MEDIA_ROOT
            system_type = None
            try:
                system = Quick.objects.filter(id=system_id)[0]
                system_type = "Quick"
                project_name = system.name
            except:
                system = File.objects.filter(id=system_id)[0]
                system_type = "File"
                project_name = system.project_name

            graph_file_name = system.slug + "_" + system.get_filename().split(".")[0] + "_sReaGraph.xgmml"
            graph_file_path = "%s/%s/%s/%s" % (media_root, system.slug, "graphs", graph_file_name)

            if not check_filepath(request, graph_file_path, system, media_root):
                if system_type == "Quick":
                    return quick_detail(request, system_id)
                else:
                    return file_detail(request, system_id)

            pickled_rxncon_system = Rxncon_system.objects.get(project_id=system_id, project_type=system_type)
            rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)

            graph = regulatory_graph.SpeciesReactionGraph(rxncon_system=rxncon_system).to_graph()

            xgmml_graph = graphML.XGMML(graph, system.slug)
            graph_file = xgmml_graph.to_file(graph_file_path)
            graph_string = xgmml_graph.to_string()

            if request.FILES.get('template'):
                graph_string = apply_template_layout(request, graph_file_path, graph_string)

            g = Graph_from_File(project_name=project_name, graph_file=graph_file_path, graph_string=graph_string,
                                comment=request.POST.get('comment'))
            g.save()
            messages.info(request, "Species reaction graph for project '" + g.project_name + "' successfully created.")
            if system_type == "Quick":
                Quick.objects.filter(id=system_id).update(sRea_graph=g)
                return quick_detail(request, system_id)
            else:
                File.objects.filter(id=system_id).update(sRea_graph=g)
                return file_detail(request, system_id)


def graph_delete(request, pk):
    f = get_object_or_404(Graph_from_File, pk=pk)
    project_name = f.project_name
    timestamp = f.timestamp
    filename = f.get_filename()
    system_type = None
    try:
        if File.objects.filter(reg_graph=f):
            id = File.objects.filter(reg_graph=f)[0].id
        elif File.objects.filter(rea_graph=f):
            id = File.objects.filter(rea_graph=f)[0].id
        else:
            id = File.objects.filter(sRea_graph=f)[0].id

    except:
        if Quick.objects.filter(reg_graph=f):
            id = Quick.objects.filter(reg_graph=f)[0].id
        elif Quick.objects.filter(rea_graph=f):
            id = Quick.objects.filter(rea_graph=f)[0].id
        else:
            id = Quick.objects.filter(sRea_graph=f)[0].id
        system_type = "Quick"

    slug = f.slug
    if request.method == 'POST':
        form = DeleteGraphForm(request.POST, instance=f)

        if form.is_valid():  # checks CSRF
            if os.path.exists(f.graph_file.name):
                os.remove(f.graph_file.name)
            f.delete()
            messages.success(request, "Successfully deleted")
            if system_type == "Quick":
                return HttpResponseRedirect("/quick/" + str(id) + "/")  # wherever to go after deleting

            else:
                return HttpResponseRedirect("/files/" + str(id) + "/")  # wherever to go after deleting
    else:
        form = DeleteGraphForm(instance=f)
    template_vars = {'form': form,
                     'project_name': project_name,
                     "timestamp": timestamp,
                     "file": filename,
                     }
    return render(request, 'graph_delete.html', template_vars)
