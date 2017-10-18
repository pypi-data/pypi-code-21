from evosnap import constants


class POSDevice:
    def __init__(self,**kwargs):
        self.__order = [
            'posDeviceType', 'posDeviceConnection', 'posDeviceColour', 'posDeviceQuantity',
        ]
        self.__lower_camelcase = constants.ALL_FIELDS

        self.pos_device_type = kwargs.get('pos_device_type')
        self.pos_device_connection = kwargs.get('pos_device_connection')
        self.pos_device_colour = kwargs.get('pos_device_colour')
        self.pos_device_quantity = kwargs.get('pos_device_quantity')

    @property
    def hash_str(self):
        required = [
            'pos_device_type', 'pos_device_connection', 'pos_device_colour', 'pos_device_quantity',
        ]
        return ''.join([str(getattr(self,f)).strip() for f in required if getattr(self,f) is not None])
