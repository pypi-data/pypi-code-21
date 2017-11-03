from ldap3 import Server, Connection, NTLM, ALL
from functools import reduce

def entry_generator(username, password):
    server = Server('corsair.adit.mines.edu', use_ssl=True, get_info=ALL)
    with Connection(server, user="ADIT\\{}".format(username), password=password, authentication=NTLM, auto_bind=True, read_only=True) as conn:
        return conn.extend.standard.paged_search(
            search_base = 'ou=classrooms-win10,ou=csm computers,dc=adit,dc=mines,dc=edu',
            search_filter = '(objectclass=computer)',
            generator = True
        )

def server_generator(entries):
    def process_pairs(acc, pair):
        path, name = acc
        key, val = pair

        if key == 'CN':
            name = val
        elif key == 'OU':
            path.append(val)

        return (path, name)

    for e in entries:
        dn = e['dn']
        dn_parts = dn.split(',')
        dn_pairs = [(k,v) for k, v in [pair.split('=') for pair in dn_parts]]

        path, server_name = reduce(process_pairs, dn_pairs, ([], ''))
        path.reverse()
        yield (path, server_name)
