from ldap3 import Server, Connection, ALL, NTLM

class LDAPManager(object):
    def __init__(self,LDAPIP = None,LDAPBaseDN = None,LDAPPrefix = None):
        self.url = LDAPIP
        self.dn = LDAPBaseDN
        self.prefix = LDAPPrefix


    def login(self,user_name,user_passwd):
        server = Server(self.url, get_info=ALL)
        conn = Connection(server, user=self.prefix + user_name, password=user_passwd, authentication=NTLM)
        return conn.bind()

    def change_passwd(self,user_name,old_passwd,new_passwd):
        return False
