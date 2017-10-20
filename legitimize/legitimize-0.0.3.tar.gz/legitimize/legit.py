import re

def phone(phone: str) -> bool:
    """
    Returns if a phone number is valid or not

    >>> phone("555-555-5555")
    True

    """
    return len(re.sub(r'\D', "", phone)) == 10