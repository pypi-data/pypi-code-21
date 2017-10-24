from evosnap import constants


class PricingComponentSetting:
    def __init__(self,**kwargs):
        self.__order = [
            'ComponentName', 'Option', 'Value',
        ]
        self.__lower_camelcase = constants.ALL_FIELDS

        self.component_name = kwargs.get('component_name')
        self.option = kwargs.get('option')
        self.value = kwargs.get('value')

    @property
    def hash_str(self):
        required = [
            'component_name', 'option', 'value'
        ]
        return ''.join([str(getattr(self,f)).strip() for f in required if getattr(self,f) is not None])
