####
# bomail.util.mime_to_mailfile
#
# Converts a file in MIME format to bomail's mailfile format.
####


import sys, email, datetime, dateutil, uuid

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.addr as addr

usage_str = """
Reads a MIME email from file and writes a mailfile to stdout.
Usage:
  mime_to_mailfile.py -h        # print this help
  mime_to_mailfile.py filename
"""


def clean(s, replace_newline_with = " "):
  if s is None:
    return ""
  result = ""
  for (h, charset) in email.header.decode_header(s):
      if isinstance(h, bytes):
        try:
          result += str(h, encoding = ("utf-8" if charset is None else charset), errors = "ignore")
        except:
          result += str(h)
      elif isinstance(h, str):
        result += h
  c = replace_newline_with
  return result.replace("\r\n", c).replace("\r", c).replace("\n", c)

def clean_addrs(unclean_addr_str):
  addr_str = clean(unclean_addr_str)
  prlist = addr.str_to_pairlist(addr_str)
  return addr.pairlist_to_str(prlist)

# m is a python email.message presumably of type "text/"
def get_plain_body(m):
  charset = m.get_content_charset()
  if charset is None:
    return str(m.get_payload(decode=True))
  return str(m.get_payload(decode=True), str(charset), "ignore")

def was_sent(m, prlist):
  return any([addr.is_pair_me(pr) for pr in prlist])


# m is a python email.message object
def get_body(m):
  if m.is_multipart():
    return get_multipart_body(m)
  else:
    return get_part_body(m)

def get_multipart_body(m):
  m_type = m.get_content_type()
  if m_type == "multipart/alternative":
    parts = m.get_payload()
    part_types = [p.get_content_type() for p in parts]
    if "text/plain" in part_types:
      return get_plain_body(parts[part_types.index("text/plain")])
    elif "text/html" in part_types:
      return get_plain_body(parts[part_types.index("text/html")])
    else:
      return ""
  else:
    # do the same thing for all of these:
    # multipart/mixed
    # multipart/related 
    # multipart/digest
    # multipart/report
    # message/rfc822
    # TODO: multipiart/encrypted
    # TODO: multipart/signed: check/verify signature if we have the public key
    # others?
    return "\n".join(get_body(p) for p in m.get_payload())

def get_part_body(m):
  m_type = m.get_content_type()
  if m_type == "text/plain":
    return get_plain_body(m)
  elif m_type == "text/html":
    return get_plain_body(m)
  else:
    return ""


def get_references(m):
  m_id = get_msgid(m)
  reply_to = ""
  if 'in-reply-to' in m:
    ref = m['in-reply-to']
    try:
      ref = ref[ref.index("<")+1:]
      right = ref.index(">")
      reply_to = ref[:right].strip()
      if reply_to == m_id:
        reply_to = ""
    except ValueError:
        pass

  reflist = []
  if 'references' in m:
    refs = m['references']
    while len(refs) > 2:
      try:
        refs = refs[refs.index("<")+1:]
        right = refs.index(">")
        new_ref = refs[:right].strip()
        if new_ref not in reflist and new_ref != reply_to and new_ref != m_id:
          reflist.append(new_ref)
        refs = refs[right+1:]
      except ValueError:
        break
  if len(reply_to) > 0:
    reflist.append(reply_to)
  return ", ".join("<" + r + ">" for r in reflist)


# parse the email's date string and return a datetime object
def parse_date(s):
  if len(s) == 0:
    return datetime.datetime(9999,12,30)
  if "A.D." in s:  # remove this, is messes up the parser
    i = s.index("A.D.")
    s = s[:i] + (s[i+4:] if i+4 < len(s) else "")
  try:
    result = email.utils.parsedate_to_datetime(s)
    if result:
      return result
  except:
    pass
  return datetime.datetime(9999,12,29)

# from pymail object
def get_msgid(m):
  attempt = clean(m['message-id']).strip()
  if len(attempt) == 0:
    attempt = "couldnotfindmessageidgenerated" + email.utils.make_msgid(uuid.uuid4().hex)
  return attempt

def main(filename):
  with open(filename) as f:
    m = email.message_from_file(f)
  return get_data(m)

# m is a python email object
# return data array
def get_data(m):
  data = ["" for l in mailfile.fields]
  from_prlist = addr.str_to_pairlist(clean(m['from']))

  data[mailfile.FROM_L] = addr.pairlist_to_str(from_prlist)
  data[mailfile.TO_L] = clean_addrs(m['to'])
  data[mailfile.CC_L] = clean_addrs(m['cc'])
  data[mailfile.SUBJ_L] = clean(m['subject'])
  data[mailfile.DATE_L] = parse_date(clean(m['date'])).isoformat()
  data[mailfile.STATE_L] = "open"
  data[mailfile.MSG_ID_L] = get_msgid(m)
  data[mailfile.REFS_L] = get_references(m)
  data[mailfile.SENT_L] = str(was_sent(m, from_prlist))
  data[mailfile.BODY_L] = get_body(m)
  return data


if __name__ == "__main__":
  if "-h" in sys.argv or len(sys.argv) <= 1:
    print(usage_str)
    exit(0)
  data = main(sys.argv[1])
  s = mailfile.data_to_str(data)
  print(s)

