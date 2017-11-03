from transactionpro.import_type import ImportType


class Invoice(ImportType):
    @property
    def fields(self):
        return (
            'last_name', 'ship_to_country', 'memo', 'exchange_rate', 'bill_to_city', 'other', 'ship_method', 'due_date',
            'fax', 'ar_account', 'bill_to_state', 'ship_to_line_1', 'ship_to_line_2', 'ship_to_line_3',
            'bill_to_line_1',
            'bill_to_line_3', 'bill_to_line_2', 'ship_date', 'phone', 'serial_lot_number', 'so_ref_number', 'customer',
            'sales_tax_item', 'item', 'service_date', 'is_pending', 'bill_to_postal', 'template_name',
            'customer_account_number', 'currency', 'ship_to_postal', 'other1', 'other2', 'contact_name', 'first_name',
            'unit_of_measure', 'rep', 'ship_to_state', 'inventory_site', 'transaction_date', 'fob', 'bill_to_line_4',
            'email', 'terms', 'description', 'ship_to_line_4', 'price', 'to_be_emailed', 'item_line_class',
            'sales_tax_code', 'customer_message', 'class', 'to_be_printed', 'inventory_bin', 'ref_number',
            'ship_to_city',
            'bill_to_country', 'quantity')

    @property
    def required_fields(self):
        return 'customer', 'ref_number', 'item'
