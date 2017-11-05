import psycopg2

class Database:
 def __init__(self, base, user, password='', host='127.0.0.1', port=5432, schema=None):
  self.con = psycopg2.connect("user=%s dbname=%s password=%s host=%s port=%s" % (user, base, password, host, port))
  self.con.set_client_encoding('utf-8')
  if schema:
   self.execute('set search_path = {}'.format(schema))

 def execute(self, sql):
  q = self.con.cursor()
  psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, q)
  q.execute(sql)
  return q
 def select_all(self, sql):
  return self.execute(sql).fetchall()
 def select_line(self, sql):
  return self.execute(sql).fetchone()
 def select_one(self, sql):
  line = self.execute(sql).fetchone()
  if line and len(line) > 0:
   return line[0]
  return None
 def begin(self):
  return True
 def commit(self):
  return self.con.commit()
 def rollback(self):
  return self.con.rollback()
 def escape_string(self, str):
  return psycopg2.extensions.QuotedString(str.encode('utf8')).getquoted().decode('utf8')
