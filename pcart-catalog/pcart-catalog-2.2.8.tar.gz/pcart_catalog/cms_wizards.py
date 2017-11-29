from cms.wizards.wizard_base import Wizard
from cms.wizards.wizard_pool import wizard_pool
from django.utils.translation import ugettext_lazy as _
from .forms import AddProductForm
from .models import Product


class ProductWizard(Wizard):
    pass

product_wizard = ProductWizard(
    title=_('New product'),
    weight=200,
    form=AddProductForm,
    description=_('Create a new product'),
)

wizard_pool.register(product_wizard)
