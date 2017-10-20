import re

def phone(phone: str, pattern: int = 1) -> str:
    """
    Format a phone number to a users specifications
    1. (555) 555-5555
    2. 555-555-5555
    3. +1-555-5555555
    4. 5555555555

    phone("555-555-5555", 1)
    (555) 555-5555

    """
    phone = re.sub(r'\D', "", phone)

    if len(phone) == 10:
        return False

    if pattern == 1:
        return "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:]
    
    if pattern == 2:
        return phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]

    if pattern == 3:
        return "+1-" + phone[0:3] + "-" + phone[3:]

    return phone
            