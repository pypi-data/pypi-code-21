import os
import pickle

import rxncon.input.excel_book.excel_book as rxncon_excel
import rxncon.input.quick.quick as rxncon_quick
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from rxncon.simulation.rule_based.bngl_from_rule_based_model import bngl_from_rule_based_model
from rxncon.simulation.rule_based.rule_based_model import rule_based_model_from_rxncon

from .forms import DeleteRuleForm
from .forms import RuleForm
from .models import Rule_based_from_rxnconsys

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


def create_rxncon_system(system, system_type):
    if system_type == "File":
        try:
            book = rxncon_excel.ExcelBook(system.get_absolute_path())
        except:
            book = rxncon_excel.ExcelBook(system.get_absolute_path())
    else:
        book = rxncon_quick.Quick(system.quick_input)
    return book.rxncon_system


def check_filepath(request, file_path, file, media_root):
    if os.path.exists(file_path):
        messages.warning(request, "Rule based model files already exist. Delete first in the system's detail view.")
        return False
    elif not os.path.exists("%s/%s/%s" % (media_root, file.slug, "graphs")):
        os.makedirs("%s/%s/%s" % (media_root, file.slug, "graphs"))
        return True
    else:
        return True


def rule(request, system_id=None):
    form = RuleForm(request.POST or None)

    if not form.is_valid() and not system_id:
        context = {
            "form": form,
        }
        return render(request, "rule_form.html", context)


class Rule_based(View):
    def post(self, request, system_id=None):
        self.system_id = system_id
        self.request = request
        self.form = RuleForm(self.request.POST or None)

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

            bngl_model_filename = system.slug + "_model.bngl"
            model_path = "%s/%s/%s/%s" % (media_root, system.slug, "rule_based", bngl_model_filename)

            if not check_filepath(request, model_path, system, media_root):
                if system_type == "Quick":
                    return quick_detail(request, system_id)
                else:
                    return file_detail(request, system_id)

            pickled_rxncon_system = Rxncon_system.objects.get(project_id=system_id, project_type=system_type)
            rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)

            rbm = rule_based_model_from_rxncon(rxncon_system)
            model_str = bngl_from_rule_based_model(rbm)

            if not os.path.exists("%s/%s/%s" % (media_root, system.slug, "rule_based")):
                os.mkdir("%s/%s/%s" % (media_root, system.slug, "rule_based"))

            with open(model_path, mode='w') as f:
                f.write(model_str)

            r = Rule_based_from_rxnconsys(project_name=project_name, model_path=model_path,
                                          comment=request.POST.get('comment'))
            r.save()
            messages.info(request, "BoolNet files for project '" + r.project_name + "' successfully created.")
            if system_type == "Quick":
                Quick.objects.filter(id=system_id).update(rule_based_model=r)
                return quick_detail(request, system_id)
            else:
                File.objects.filter(id=system_id).update(rule_based_model=r)
                return file_detail(request, system_id)


def rule_based_delete(request, pk):
    f = get_object_or_404(Rule_based_from_rxnconsys, pk=pk)
    project_name = f.project_name
    timestamp = f.timestamp
    filename = f.get_model_filename()
    system_type = None
    try:
        id = File.objects.filter(rule_based_model=f)[0].id
        system_type = "File"
    except:
        id = Quick.objects.filter(rule_based_model=f)[0].id
        system_type = "Quick"

    if request.method == 'POST':
        form = DeleteRuleForm(request.POST, instance=f)

        if form.is_valid():  # checks CSRF

            if os.path.exists(f.model_path.name):
                os.remove(f.model_path.name)
            f.delete()
            messages.success(request, "Successfully deleted")
            if system_type == "Quick":
                return HttpResponseRedirect("/quick/" + str(id) + "/")  # wherever to go after deleting

            else:
                return HttpResponseRedirect("/files/" + str(id) + "/")  # wherever to go after deleting
    else:
        form = DeleteRuleForm(instance=f)
    template_vars = {'form': form,
                     'project_name': project_name,
                     "timestamp": timestamp,
                     "file": filename,
                     }
    return render(request, 'rule_delete.html', template_vars)
