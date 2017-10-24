from evosnap import constants


class PrimaryOwner:
    def __init__(self,**kwargs):
        self.__order = [
            'PrimaryOwnerPercentage', 'PrimaryOwnershipType', 'PrimaryOwnerFirstName', 'PrimaryOwnerLastName',
            'PrimaryOwnerAddress', 'PrimaryOwnerCity', 'PrimaryOwnerCounty', 'PrimaryOwnerPostalCode',
            'PrimaryOwnerCountry', 'PrimaryOwnerDOB', 'PrimaryOwnerAddress2',
            'PrimaryOwnerAddressBuildingNumber', 'PrimaryOwnerAddressFloorNumber',
            'PrimaryOwnerAddressDoorNumber', 'PrimaryOwnerHomePhonePrefix', 'PrimaryOwnerHomePhone',
            'PrimaryOwnerDocumentNumber', 'PrimaryOwnerIsOnPepList', 'PrimaryOwnerIsOnSancionList',
        ]
        self.__camelcase = constants.ALL_FIELDS

        self.primary_owner_percentage = kwargs.get('primary_owner_percentage')
        self.primary_ownership_type = kwargs.get('primary_ownership_type')
        self.primary_owner_first_name = kwargs.get('primary_owner_first_name')
        self.primary_owner_last_name = kwargs.get('primary_owner_last_name')
        self.primary_owner_address = kwargs.get('primary_owner_address')
        self.primary_owner_city = kwargs.get('primary_owner_city')
        self.primary_owner_county = kwargs.get('primary_owner_county')
        self.primary_owner_postal_code = kwargs.get('primary_owner_postal_code')
        self.primary_owner_country = kwargs.get('primary_owner_country')
        self.primary_owner_d_o_b = kwargs.get('primary_owner_d_o_b')
        self.primary_owner_address2 = kwargs.get('primary_owner_address2')
        self.primary_owner_address_building_number = kwargs.get('primary_owner_address_building_number')
        self.primary_owner_address_floor_number = kwargs.get('primary_owner_address_floor_number')
        self.primary_owner_address_door_number = kwargs.get('primary_owner_address_door_number')
        self.primary_owner_home_phone_prefix = kwargs.get('primary_owner_home_phone_prefix')
        self.primary_owner_home_phone = kwargs.get('primary_owner_home_phone')
        self.primary_owner_document_number = kwargs.get('primary_owner_document_number')
        self.primary_owner_is_on_pep_list = kwargs.get('primary_owner_is_on_pep_list')
        self.primary_owner_is_on_sancion_list = kwargs.get('primary_owner_is_on_sancion_list')

    @property
    def hash_str(self):
        required = [
            'primary_owner_percentage', 'primary_ownership_type', 'primary_owner_first_name', 'primary_owner_last_name',
            'primary_owner_address', 'primary_owner_city', 'primary_owner_county', 'primary_owner_postal_code',
            'primary_owner_country', 'primary_owner_d_o_b', 'primary_owner_address2',
            'primary_owner_address_building_number', 'primary_owner_address_floor_number',
            'primary_owner_address_door_number', 'primary_owner_home_phone_prefix', 'primary_owner_home_phone',
            'primary_owner_document_number', 'primary_owner_is_on_pep_list', 'primary_owner_is_on_sancion_list',
        ]
        return ''.join([str(getattr(self,f)).strip() for f in required if getattr(self,f) is not None])