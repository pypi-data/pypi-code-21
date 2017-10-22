def make_resource_search_column(server_address: str, server_name: str, display_url: str, resource_port: int):
    """
    Generate column for ORM model `resources.search`
    IP / DOMAIN, NAME, DISPLAY_URL
    :return: str
    """
    from findex_common.static_variables import DefaultPorts
    try:
        protocol = DefaultPorts().name_by_id(resource_port).lower()
    except:
        protocol = ""
    server_address_spl = server_address.split(".")
    server_address_spl = " ".join([z for z in server_address_spl \
                                   if not z.isdigit() and len(z) >= 2])
    rtn = "%s %s %s %s %s" % (server_address, server_address_spl,
                              server_name, display_url, protocol)
    return " ".join([z for z in rtn.split(" ") if z])
