""" Custom AT widgets
"""
from Products.Archetypes.Registry import registerWidget
from eea.forms.widgets.ManagementPlanWidget import ManagementPlanWidget
from eea.forms.widgets.QuickUploadWidget import QuickUploadWidget

def register():
    """ Custom AT registrations
    """
    registerWidget(ManagementPlanWidget,
        title='EEA Management Plan Code',
        description=('Renders a HTML selection widget, to'
                     ' allow you enter the year and the'
                     ' EEA management plan code'),
        used_for=(
            'eea.forms.fields.ManagementPlanField.ManagementPlanField'))

    registerWidget(QuickUploadWidget,
        title='EEA Quick Upload',
        description=("Allows you to drag&drop files directly "
                     "from your computer's Desktop")
        )
