import hashlib
import random
import string
import uuid




def string_generator(size=6, digits_only=False):
    """
    Generates a random string with Capital letters and digits

    :param int size: The length of the string
    :param bool digits_only: Does the string contains digits only, or also chars
    :return string: A random string
    """
    if digits_only:
        chars = string.digits
    else:
        chars = string.digits + string.ascii_uppercase
    return ''.join(random.choice(chars) for _ in range(size))


existing_mac_list = []


def gen_random_mac():
    """
    Generates a random MAC address in the form: ac:87:a3:38:70:1a.
    We call -  global existing_mac_list - to make sure no MAC address is generated twice on the same run

    :return string mac_str: MAC address
    """
    global existing_mac_list
    # Generate MAC addresses until a unique one is found
    while True:
        mac = [random.randint(0x00, 0xff) for i in range(6)]
        mac_str = ':'.join(map(lambda x: "%02x" % x, mac))

        # Make sure we are not using this MAC already
        if mac_str not in existing_mac_list:
            existing_mac_list.append(mac_str)
            return mac_str


def gen_random_local_ip(base_ip, ip_list, subnet_fields=1):
    """
    Generates a random local IP address.

    :param string base_ip: the base local IP: "192.168.0.1"
    :param list ip_list: A list of all current IPs, we check that the new IP is not in the list
    :param int subnet_fields: How many fields for change (1-4), 1 is the Lower Octet: (192.168.0.X)

    :return string ip: A random IP in the received subnet and IP address
    """
    max_host_num = 30

    ip_fields = base_ip.split(".")
    if len(ip_fields) != 4 or subnet_fields > 4:
        raise ValueError("Wrong random IP inputs %s, %s" % (base_ip, subnet_fields))
    # Check the we are not exceeding teh valid IP number
    if len(ip_list) == max_host_num or len(ip_list) == (255**subnet_fields - 2):
        raise ValueError("Too many hosts for a single AP")
    # Generate an IP address until a new one is found
    while True:
        for i in range(subnet_fields):
            # Lower octet is 2-254, others are 0-255
            if subnet_fields == 1:
                ip_fields[len(ip_fields) - 1 - i] = str(random.randint(2, 254))
            else:
                ip_fields[len(ip_fields) - 1 - i] = str(random.randint(0, 255))
        ip = ".".join(ip_fields)
        # make sure that we are not using this MAC already
        if ip not in ip_list:
            ip_list.append(ip)
            return ip


def gen_random_ip():
    """
    Generate a random IP address: X.X.X.X starting in 1.0.0.1

    :return string ip: A random IP
    """
    ip = [random.randint(1, 255),
          random.randint(0, 255),
          random.randint(0, 255),
          random.randint(1, 255)]
    return '.'.join(map(lambda x: "%s" % x, ip))


def gen_random_id(id_list, base_id=1):
    """
    Generates a random AP interface ID in the format: ID=1_X,
    :param int base_id: The ID header (1)
    :param list id_list: A list of all current IDs, we check that the new IP is not in the list
    """
    max_num_of_ids = 3
    min_id = 1
    max_id = 9

    if len(id_list) == max_num_of_ids:
        raise ValueError("Too many hosts for a single AP")

    x = 0
    while x < max_id:
        # 1_X
        if_id = str(base_id) + "_" + str(random.randint(min_id, max_id))
        # make sure that we are not using this MAC already
        if if_id not in id_list:
            id_list.append(if_id)
            return if_id
        x += 1
    # Raise an exception upon failure
    raise ValueError("Couldn't create a random ID")


def id_generator(size=6, chars=string.digits):
    """
    Generates a random string with digits only

    :param int size: The length of the string
    :param list chars: The chars to generate strings from (digits)
    :return string: A random string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def generate_random_item_id(size=6):
    """
    Generates a random UUID based on a seed and the current timestamp

    :param int size: The length of the string
    """
    # Get a string random UUID
    serial = str(uuid.uuid1())
    # Hash the UUID for further scrambling
    encoded = hashlib.sha1(serial.encode("utf8"))
    hashed_id = encoded.hexdigest()
    if size <= len(hashed_id):
        return hashed_id[:size]
    else:
        return hashed_id
