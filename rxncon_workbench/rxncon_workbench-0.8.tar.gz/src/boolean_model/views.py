import os
import pickle

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from rxncon.simulation.boolean.boolean_model import SmoothingStrategy, KnockoutStrategy, OverexpressionStrategy
from rxncon.simulation.boolean.boolnet_from_boolean_model import QuantitativeContingencyStrategy, \
    boolnet_strs_from_rxncon

from .forms import BoolForm
from .forms import DeleteBoolForm
from .models import Bool_from_rxnconsys

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


def check_filepath(request, file_path, file, media_root):
    if os.path.exists(file_path):
        messages.warning(request, "Boolean model files already exist. Delete first in the system's detail view.")
        return False
    elif not os.path.exists("%s/%s/%s" % (media_root, file.slug, "graphs")):
        os.makedirs("%s/%s/%s" % (media_root, file.slug, "graphs"))
        return True
    else:
        return True


def bool(request, system_id=None):
    form = BoolForm(request.POST or None)

    if not form.is_valid() and not system_id:
        context = {
            "form": form,
        }
        return render(request, "bool_form.html", context)


class Bool(View):
    def post(self, request, system_id=None):
        self.system_id = system_id
        self.request = request
        self.form = BoolForm(self.request.POST or None)

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

            boolnet_model_filename = system.slug + "_model.boolnet"
            boolnet_symbol_filename = system.slug + "_symbols.csv"
            boolnet_initial_val_filename = system.slug + "_initial_vals.csv"

            model_path = "%s/%s/%s/%s" % (media_root, system.slug, "boolnet", boolnet_model_filename)
            symbol_path = "%s/%s/%s/%s" % (media_root, system.slug, "boolnet", boolnet_symbol_filename)
            init_path = "%s/%s/%s/%s" % (media_root, system.slug, "boolnet", boolnet_initial_val_filename)

            for path in [model_path, symbol_path, init_path]:
                if not check_filepath(request, path, system, media_root):
                    if system_type == "Quick":
                        return quick_detail(request, system_id)
                    else:
                        return file_detail(request, system_id)

            pickled_rxncon_system = Rxncon_system.objects.get(project_id=system_id, project_type=system_type)
            rxncon_system = pickle.loads(pickled_rxncon_system.pickled_system)

            smoothing = SmoothingStrategy(request.POST.get('smoothing'))
            knockout = KnockoutStrategy(request.POST.get('knockout'))
            overexpr = OverexpressionStrategy(request.POST.get('overexpr'))
            k_plus = QuantitativeContingencyStrategy(request.POST.get('k_plus'))
            k_minus = QuantitativeContingencyStrategy(request.POST.get('k_minus'))
            model_str, symbol_str, initial_val_str = boolnet_strs_from_rxncon(rxncon_system,
                                                                              smoothing_strategy=smoothing,
                                                                              knockout_strategy=knockout,
                                                                              overexpression_strategy=overexpr,
                                                                              k_plus_strategy=k_plus,
                                                                              k_minus_strategy=k_minus)

            if not os.path.exists("%s/%s/%s" % (media_root, system.slug, "boolnet")):
                os.mkdir("%s/%s/%s" % (media_root, system.slug, "boolnet"))

            with open(model_path, mode='w') as f:
                f.write(model_str)

            with open(symbol_path, mode='w') as f:
                f.write(symbol_str)

            with open(init_path, mode='w') as f:
                f.write(initial_val_str)

            b = Bool_from_rxnconsys(project_name=project_name, model_path=model_path, symbol_path=symbol_path,
                                    init_path=init_path,
                                    comment=request.POST.get('comment'))
            b.save()
            messages.info(request, "BoolNet files for project '" + b.project_name + "' successfully created.")
            if system_type == "Quick":
                Quick.objects.filter(id=system_id).update(boolean_model=b)
                return quick_detail(request, system_id)
            else:
                File.objects.filter(id=system_id).update(boolean_model=b)
                return file_detail(request, system_id)


def bool_delete(request, pk):
    f = get_object_or_404(Bool_from_rxnconsys, pk=pk)
    project_name = f.project_name
    timestamp = f.timestamp
    system_type = None
    try:
        id = File.objects.filter(boolean_model=f)[0].id
        system_type = "File"
    except:
        id = Quick.objects.filter(boolean_model=f)[0].id
        system_type = "Quick"

    slug = f.slug
    if request.method == 'POST':
        form = DeleteBoolForm(request.POST, instance=f)

        if form.is_valid():  # checks CSRF

            if os.path.exists(f.model_path.name):
                os.remove(f.model_path.name)
                os.remove(f.symbol_path.name)
                os.remove(f.init_path.name)
            f.delete()
            messages.success(request, "Tree files Successfully deleted.")
            if system_type == "Quick":
                return HttpResponseRedirect("/quick/" + str(id) + "/")  # wherever to go after deleting

            else:
                return HttpResponseRedirect("/files/" + str(id) + "/")  # wherever to go after deleting
    else:
        form = DeleteBoolForm(instance=f)
    template_vars = {'form': form,
                     'project_name': project_name,
                     "timestamp": timestamp
                     }
    return render(request, 'bool_delete.html', template_vars)
