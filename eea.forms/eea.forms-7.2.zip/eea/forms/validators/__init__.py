""" Validators
"""
from Products.validation import validation
from eea.forms.validators.managementplan import ManagementPlanCodeValidator

def register():
    """ Custom AT validators
    """
    validation.register(
        ManagementPlanCodeValidator('management_plan_code_validator'))
