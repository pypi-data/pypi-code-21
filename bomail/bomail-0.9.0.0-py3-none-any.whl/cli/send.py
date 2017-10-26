####
# bomail.cli.send
#
# Send drafts.
####

import os
import sys
import mimetypes
import subprocess, email
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

import bomail.config.config as config
import bomail.cli.mailfile as mailfile
import bomail.util.addr as addr

usage_str = """
Reads filename(s) from stdin one per line and sends them.
send.py -h to print this help.
"""


# adapted from python library example: https://docs.python.org/3/library/email-examples.html
def add_attachments(msg, attach_list):
  for filename in attach_list:
    if not os.path.exists(filename):
      raise Exception("Did not send. Could not attach (does not exist): " + filename)
    if not os.path.isfile(filename):
      raise Exception("Did not send. Could not attach (is not a file): " + filename)
    ctype, encoding = mimetypes.guess_type(filename)
    if ctype is None or encoding is not None:
      ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
      with open(filename) as fp:
        sub_msg = MIMEText(fp.read(), _subtype=subtype)
    elif maintype == 'image':
      with open(filename, 'rb') as fp:
        sub_msg = MIMEImage(fp.read(), _subtype=subtype)
    elif maintype == 'audio':
      with open(filename, 'rb') as fp:
        sub_msg = MIMEAudio(fp.read(), _subtype=subtype)
    else:
      with open(filename, 'rb') as fp:
        sub_msg = MIMEBase(maintype, subtype)
        sub_msg.set_payload(fp.read())
      encoders.encode_base64(sub_msg)
    sub_msg.add_header('Content-Disposition', 'attachment', filename=os.path.split(filename)[1])
    msg.attach(sub_msg)


# return num_successes, err_msg
def main(filelist, mgr):
  try:
    serv = smtplib.SMTP(config.smtp_servername, config.smtp_port)
    serv.ehlo()
    serv.starttls()
    serv.ehlo()
    serv.login(config.email_addr, config.password)
  except Exception as e:
    return 0, "Error connecting to server: " + str(e)

  for i, filename in enumerate(filelist):
    data = mgr.get_all(filename)
    attach_s = data[mailfile.ATTACH_L].strip()
    if len(attach_s) == 0:  # no attachments
      msg = MIMEText(data[mailfile.BODY_L], 'plain')
    else:
      msg = MIMEMultipart()
      msg.attach(MIMEText(data[mailfile.BODY_L], 'plain'))
      add_attachments(msg, attach_s.split(", "))
    msg['Subject'] = data[mailfile.SUBJ_L]
    msg['From'] = data[mailfile.FROM_L]
    msg['To'] = data[mailfile.TO_L]
    msg['CC'] = data[mailfile.CC_L]
    refs = data[mailfile.REFS_L]
    if len(refs) > 0:
      msg['In-Reply-To'] = refs.split(", ")[-1]
      msg['References'] = refs
    recip_lists = data[mailfile.TO_L].split(", ")
    if len(data[mailfile.CC_L]) > 0:
      recip_lists += data[mailfile.CC_L].split(", ")
    if len(data[mailfile.BCC_L]) > 0:
      recip_lists += data[mailfile.BCC_L].split(", ")
    recip_addrs = [addr.str_to_pair(a)[1] for a in recip_lists]

    try:
      serv.sendmail(config.email_addr, recip_addrs, msg.as_string())
    except Exception as e:
      serv.quit()
      return i, "Error sending message #" + str(i) + " [" + filename + "]: " + str(e)

  serv.quit()
  return len(filelist), ""


def main_cli():
  if len(sys.argv) >= 2:
    print(usage_str)
    exit(0)

  filelist = [f.strip() for f in sys.stdin.readlines()]
  res, err = main(filelist, mailfile.MailMgr())
  print("Sent " + str(res) + "/" + str(len(filelist)) + " messages.")
  if res < len(filelist):
    print(err)


if __name__ == "__main__":
  main_cli()


