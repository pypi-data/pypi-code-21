import pypandoc
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import os

import argparse


def send_email(url, output, subject, body, email_addresses):
    pypandoc.convert(url, 'pdf', outputfile=output,
                     extra_args=['-V', 'geometry:margin=1.5cm'])
    username = 'updatewpy@gmail.com'
    password = 'pass1pass1234'
    to = 'arnzent1@mymail.nku.edu'

    to = email_addresses
    if "," in to:
        ' ,'.join("'{0}'".format(x) for x in to)

    message = MIMEMultipart()
    message['From'] = username
    message['To'] = "[" + to + "]"
    message['Subject'] = subject.capitalize()
    body = body + "\n\n\n" + "Email sent from wikiPy."

    body_send = MIMEText(body, 'plain')
    message.attach(body_send)

    element = MIMEBase('application', "octet-stream")
    element.set_payload(open(output, "rb").read())
    encoders.encode_base64(element)
    element.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(output))
    message.attach(element)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(username, to, message.as_string())
    server.close()
    return True


def convert_markdown_PDF(location, output):
    pypandoc.convert(location, 'pdf', outputfile=output, extra_args=['-V', 'geometry:margin=1.5cm'])

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-action', help='Select action - "-convert" or "-email"')
    parser.add_argument('-location', help='Enter the location of the markdown file to be converted to a PDF.')
    parser.add_argument('-output', help='Enter the location where the converted markdown file will be placed.')
    parser.add_argument('-subject', help='Enter the subject of the email.')
    parser.add_argument('-body', help='Enter the content of the email.')
    parser.add_argument('-recipients', help='Enter the recipients of the email message. (Multiple addresses separated by commas - check@check.com, check_two@check.com')

    counter = 0
    message = '\n'

    args = parser.parse_args()
    if args.action == 'convert':

        if args.location is not None:
            # Check to see if the selected file exists.
            if os.path.isfile(args.location):
                counter = counter + 1
            else:
                message = message + 'File does not exists.\n'
        else:
            message = message + 'Enter the location of the markdown file.\n'

        if args.output is not None:
            counter = counter + 1
        else:
            message = message + 'Enter an output location for the converted file.\n'

        if counter == 2:

            convert_markdown_PDF(args.location, args.output)

        else:
            print(message)


    if args.action == 'email':

        if args.location is not None:
            # Check to see if the selected file exists.
            if os.path.isfile(args.location):
                counter = counter + 1
            else:
                message = message + 'File does not exists.\n'
        else:
            message = message + 'Enter the location of the markdown file.\n'

        if args.output is not None:
            counter = counter + 1
        else:
            message = message + 'Enter a name for the PDF file.\n'

        if counter == 2:

            subject = ''
            body = ''
            recipients = ''

            if args.subject is not None:
                subject = args.subject

            if args.body is not None:
                body = args.body

            if args.recipients is not None:
                recipients = args.recipients

            send_email(args.location, args.output, subject, body, recipients)

        else:
            print(message)

    if counter is not 2:
        print('\nSelect action - "-action convert" or "-action email"')


if __name__ == "__main__":
    Main()