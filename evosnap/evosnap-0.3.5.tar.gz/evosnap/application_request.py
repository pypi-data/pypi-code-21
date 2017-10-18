import base64
import hashlib
import hmac
import json
import requests

from evosnap.response import Response
from evosnap.data_element_encoder import DataElementEncoder
from evosnap.exceptions import ApplicationRequestException


class MerchantApplicationRequest():
    def __init__(self, **kwargs):
        """
        Basic information about the check being processed. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.__order = [
            'HashValue',
            'IntegratorID', 'ReferenceID', 'OriginIPAddress', 'CultureCode', 'Email', 'URL',
            'ApplicationType', 'CompanyName', 'RegisteredCompanyName', 'ContactFirstName', 'ContactLastName',
            'ContactPostalCode', 'PhysicalAddress', 'PhysicalCity', 'PhysicalCounty', 'PhysicalPostalCode',
            'PhysicalCountry', 'PhysicalPhone', 'BusinessStructureTypeId', 'MerchantCategoryCode',
            'CompanyObjective', 'VATID', 'BankName', 'BankAccountHolderName', 'IBAN',
            'BankBICSWIFT', 'InvoiceBankName', 'InvoiceBankAccountOwner', 'InvoiceBankIBAN',
            'InvoiceBankAddress1', 'InvoiceBankCity', 'InvoiceBankCountry', 'ForecastMaxTicketSizeAmount',
            'ForecastAllVolume', 'ForecastAveTicketSizeAmount', 'ForecastRefundPercentage',
            'PSPaidInAdvanceTF', 'PSPaidInAdvanceAvgAnnualPercentage',
            'PSPaidInAdvanceAvgDeliveryDays', 'PCIHasSAQ', 'PCIThirdPartyRemotes',
            'PCICardDataStored', 'PCIHadDataCompromise', 'NoVat', 'PrimaryOwnerArray',
            'ProductPackageID', 'OtherServicesMOTO', 'OtherServicesSettlement',
            'OtherServicesAMEXRouting', 'OtherServicesSnapEcommerce', 'OtherServicesChargebacks',
            'OtherServicesRecurringPayments', 'OtherServicesChinaUnionPay', 'OtherServices3DSecure',
            'OtherServicesCashback', 'OtherServicesPremiumService', 'OtherServicesDCC',
            'OtherServicesReceiptLogo', 'OtherServicesTipp', 'OtherServicesMonths',
            'OtherServicesMonthsDeclaration', 'OtherServicesCVV', 'ecommDeployment', 'posDeploymentArray',
            'InvoiceBankAddress2', 'InvoiceBankAddressFloorNumber', 'InvoiceBankAddressDoorNumber',
            'InvoiceBankAddressBuildingNumber', 'InvoiceBankZip', 'DocumentationVersion'
        ]
        self.__camelcase = [
            'hash_value',
            'integrator_i_d', 'reference_i_d', 'origin_i_p_address', 'culture_code', 'email', 'u_r_l',
            'application_type', 'company_name', 'registered_company_name', 'contact_first_name', 'contact_last_name',
            'contact_postal_code', 'physical_address', 'physical_city', 'physical_county', 'physical_postal_code',
            'physical_country', 'physical_phone', 'business_structure_type_id', 'merchant_category_code',
            'company_objective', 'v_a_t_i_d', 'bank_name', 'bank_account_holder_name', 'i_b_a_n',
            'bank_b_i_c_s_w_i_f_t', 'invoice_bank_name', 'invoice_bank_account_owner', 'invoice_bank_i_b_a_n',
            'invoice_bank_address1', 'invoice_bank_city', 'invoice_bank_country', 'forecast_max_ticket_size_amount',
            'forecast_all_volume', 'forecast_ave_ticket_size_amount', 'forecast_refund_percentage',
            'p_s_paid_in_advance_t_f', 'p_s_paid_in_advance_avg_annual_percentage',
            'p_s_paid_in_advance_avg_delivery_days', 'p_c_i_has_s_a_q', 'p_c_i_third_party_remotes',
            'p_c_i_card_data_stored', 'p_c_i_had_data_compromise', 'no_vat', 'primary_owner_array',
            'product_package_i_d', 'other_services_m_o_t_o', 'other_services_settlement',
            'other_services_a_m_e_x_routing', 'other_services_snap_ecommerce', 'other_services_chargebacks',
            'other_services_recurring_payments', 'other_services_china_union_pay', 'other_services_3_d_secure',
            'other_services_cashback', 'other_services_premium_service', 'other_services_d_c_c',
            'other_services_receipt_logo', 'other_services_tipp', 'other_services_months',
            'other_services_months_declaration', 'other_services_c_v_v', 'invoice_bank_address2',
            'invoice_bank_address_floor_number', 'invoice_bank_address_door_number',
            'invoice_bank_address_building_number', 'invoice_bank_zip', 'documentation_version'
        ]
        self.__lower_camelcase = ['ecomm_deployment', 'pos_deployment_array']
        self.__exclude = ['ssl_verification', 'request_method', 'mas_baseurl', 'secret']

        self.ssl_verification = kwargs.get('ssl_verification', True)
        self.request_method = 'POST'

        self.mas_baseurl = kwargs.get('mas_baseurl', 'https://api.certification.boipa.com/MAS/api/v1/Submit')
        self.secret = kwargs.get('secret')

        # REQUIRED
        self.integrator_i_d = kwargs.get('integrator_i_d')
        self.reference_i_d = kwargs.get('reference_i_d')
        self.origin_i_p_address = kwargs.get('origin_i_p_address')
        self.culture_code = kwargs.get('culture_code')
        self.email = kwargs.get('email')
        self.u_r_l = kwargs.get('u_r_l')
        self.application_type = kwargs.get('application_type')
        self.company_name = kwargs.get('company_name')
        self.registered_company_name = kwargs.get('registered_company_name')
        self.contact_first_name = kwargs.get('contact_first_name')
        self.contact_last_name = kwargs.get('contact_last_name')
        self.contact_postal_code = kwargs.get('contact_postal_code')
        self.physical_address = kwargs.get('physical_address')
        self.physical_city = kwargs.get('physical_city')
        self.physical_county = kwargs.get('physical_county')
        self.physical_postal_code = kwargs.get('physical_postal_code')
        self.physical_country = kwargs.get('physical_country')
        self.physical_phone = kwargs.get('physical_phone')
        self.business_structure_type_id = kwargs.get('business_structure_type_id')
        self.merchant_category_code = kwargs.get('merchant_category_code')
        self.company_objective = kwargs.get('company_objective')
        self.v_a_t_i_d = kwargs.get('v_a_t_i_d')
        self.bank_name = kwargs.get('bank_name')
        self.bank_account_holder_name = kwargs.get('bank_account_holder_name')
        self.i_b_a_n = kwargs.get('i_b_a_n')
        self.bank_b_i_c_s_w_i_f_t = kwargs.get('bank_b_i_c_s_w_i_f_t')
        self.invoice_bank_name = kwargs.get('invoice_bank_name')
        self.invoice_bank_account_owner = kwargs.get('invoice_bank_account_owner')
        self.invoice_bank_i_b_a_n = kwargs.get('invoice_bank_i_b_a_n')
        self.invoice_bank_address1 = kwargs.get('invoice_bank_address1')
        self.invoice_bank_city = kwargs.get('invoice_bank_city')
        self.invoice_bank_country = kwargs.get('invoice_bank_country')
        self.forecast_max_ticket_size_amount = kwargs.get('forecast_max_ticket_size_amount')
        self.forecast_all_volume = kwargs.get('forecast_all_volume')
        self.forecast_ave_ticket_size_amount = kwargs.get('forecast_ave_ticket_size_amount')
        self.forecast_refund_percentage = kwargs.get('forecast_refund_percentage')
        self.p_s_paid_in_advance_t_f = kwargs.get('p_s_paid_in_advance_t_f')
        self.p_s_paid_in_advance_avg_annual_percentage = kwargs.get('p_s_paid_in_advance_avg_annual_percentage')
        self.p_s_paid_in_advance_avg_delivery_days = kwargs.get('p_s_paid_in_advance_avg_delivery_days')
        self.p_c_i_has_s_a_q = kwargs.get('p_c_i_has_s_a_q')
        self.p_c_i_third_party_remotes = kwargs.get('p_c_i_third_party_remotes')
        self.p_c_i_card_data_stored = kwargs.get('p_c_i_card_data_stored')
        self.p_c_i_had_data_compromise = kwargs.get('p_c_i_had_data_compromise')
        self.no_vat = kwargs.get('no_vat')
        self.primary_owner_array = kwargs.get('primary_owner_array')
        self.product_package_i_d = kwargs.get('product_package_i_d')
        self.other_services_m_o_t_o = kwargs.get('other_services_m_o_t_o')
        self.other_services_settlement = kwargs.get('other_services_settlement')
        self.other_services_a_m_e_x_routing = kwargs.get('other_services_a_m_e_x_routing')
        self.other_services_snap_ecommerce = kwargs.get('other_services_snap_ecommerce')
        self.other_services_chargebacks = kwargs.get('other_services_chargebacks')
        self.other_services_recurring_payments = kwargs.get('other_services_recurring_payments')
        self.other_services_china_union_pay = kwargs.get('other_services_china_union_pay')
        self.other_services_3_d_secure = kwargs.get('other_services_3_d_secure')
        self.other_services_cashback = kwargs.get('other_services_cashback')
        self.other_services_premium_service = kwargs.get('other_services_premium_service')
        self.other_services_d_c_c = kwargs.get('other_services_d_c_c')
        self.other_services_receipt_logo = kwargs.get('other_services_receipt_logo')
        self.other_services_tipp = kwargs.get('other_services_tipp')
        self.other_services_months = kwargs.get('other_services_months')
        self.other_services_months_declaration = kwargs.get('other_services_months_declaration')
        self.other_services_c_v_v = kwargs.get('other_services_c_v_v')
        self.ecomm_deployment = kwargs.get('ecomm_deployment')
        self.pos_deployment_array = kwargs.get('pos_deployment_array')

        # OPTIONAL
        self.invoice_bank_address2 = kwargs.get('invoice_bank_address2')
        self.invoice_bank_address_floor_number = kwargs.get('invoice_bank_address_floor_number')
        self.invoice_bank_address_door_number = kwargs.get('invoice_bank_address_door_number')
        self.invoice_bank_address_building_number = kwargs.get('invoice_bank_address_building_number')
        self.invoice_bank_zip = kwargs.get('invoice_bank_zip')
        self.documentation_version = kwargs.get('documentation_version')

        self.hash_value = self.hash

    @property
    def request_json(self):
        return json.dumps(self, cls=DataElementEncoder)

    @property
    def pretty_json(self):
        return json.dumps(self, cls=DataElementEncoder, indent=4)

    @property
    def primary_owner_array_hash(self):
        return ''.join([f.hash_str for f in self.primary_owner_array])

    @property
    def pos_deployment_array_hash(self):
        return ''.join([f.hash_str for f in self.pos_deployment_array])

    @property
    def hash_str(self):
        required = [
            'integrator_i_d', 'reference_i_d', 'origin_i_p_address', 'culture_code', 'email', 'u_r_l',
            'application_type', 'company_name', 'registered_company_name', 'contact_first_name', 'contact_last_name',
            'contact_postal_code', 'physical_address', 'physical_city', 'physical_county', 'physical_postal_code',
            'physical_country', 'physical_phone', 'business_structure_type_id', 'merchant_category_code',
            'company_objective', 'v_a_t_i_d', 'bank_name', 'bank_account_holder_name', 'i_b_a_n',
            'bank_b_i_c_s_w_i_f_t', 'invoice_bank_name', 'invoice_bank_account_owner', 'invoice_bank_i_b_a_n',
            'invoice_bank_address1', 'invoice_bank_city', 'invoice_bank_country', 'forecast_max_ticket_size_amount',
            'forecast_all_volume', 'forecast_ave_ticket_size_amount', 'forecast_refund_percentage',
            'p_s_paid_in_advance_t_f', 'p_s_paid_in_advance_avg_annual_percentage',
            'p_s_paid_in_advance_avg_delivery_days', 'p_c_i_has_s_a_q', 'p_c_i_third_party_remotes',
            'p_c_i_card_data_stored', 'p_c_i_had_data_compromise', 'no_vat', 'primary_owner_array_hash',
            'product_package_i_d', 'other_services_m_o_t_o', 'other_services_settlement',
            'other_services_a_m_e_x_routing', 'other_services_snap_ecommerce', 'other_services_chargebacks',
            'other_services_recurring_payments', 'other_services_china_union_pay', 'other_services_3_d_secure',
            'other_services_cashback', 'other_services_premium_service', 'other_services_d_c_c',
            'other_services_receipt_logo', 'other_services_tipp', 'other_services_months',
            'other_services_months_declaration', 'other_services_c_v_v', 'ecomm_deployment',
            'pos_deployment_array_hash', 'invoice_bank_address2',
            'invoice_bank_address_floor_number', 'invoice_bank_address_door_number',
            'invoice_bank_address_building_number', 'invoice_bank_zip', 'documentation_version'
        ]

        return ''.join([str(getattr(self,f)).strip() for f in required if getattr(self,f) is not None])


    @property
    def hash(self):
        h = hmac.new(
            bytes.fromhex(self.secret),
            msg=self.hash_str.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        dig = h.digest()
        return base64.b64encode(dig).decode('utf-8')


    @property
    def request_endpoint(self):
        return self.mas_baseurl

    def send(self, test_request=None):
        response = requests.request(
            method=self.request_method,
            url=self.request_endpoint,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            data=self.request_json if not test_request else json.dumps(test_request),
            verify=self.ssl_verification
        )
        if response.status_code!=200 and response.status_code!=201 and response.status_code!=400:
            try:
                msg = str(response.status_code)+' '+Response(response.text).to_pretty_json()
                raise ApplicationRequestException(msg)
            except json.JSONDecodeError:
                msg = str(response.status_code) + ' ' + response.text
                raise ApplicationRequestException(msg)
        return Response(response.text)