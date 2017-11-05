class DeliveryError(Exception):
    pass


class PaymentError(Exception):
    pass


class ProductError(Exception):
    pass


class ProductQuantityError(ProductError):
    pass
