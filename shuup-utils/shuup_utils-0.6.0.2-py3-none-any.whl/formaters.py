import ipaddress

from django.utils.ipv6 import clean_ipv6_address


def clean_ip(ip_address: str) -> str:
    """
    Because django uses `clean_ipv6_address` in the response render.
    """
    is_ipv6 = ipaddress.ip_address(ip_address).version == 6
    if is_ipv6:
        return clean_ipv6_address(ip_address)
    else:
        return ip_address
