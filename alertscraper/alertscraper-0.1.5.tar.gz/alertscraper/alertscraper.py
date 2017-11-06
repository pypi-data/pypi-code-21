from pyquery import PyQuery
import argparse
import os
import re
import sys
import datetime

_is_verbose = False
parser = None


class ArgError(ValueError):
    pass


def parse_args(argv):
    global parser
    parser = argparse.ArgumentParser(
        prog='alertscraper',
        description='Flexible tool for scraping for certain certain '
        'DOM elements, and then emailing if new ones are added.',
    )

    parser.add_argument('-n', '--dryrun', help='dryrun, just simulate',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument('-H', '--html', help='output html',
                        action='store_true')
    parser.add_argument('-e', '--email', help='output results to email')
    parser.add_argument('-f', '--file', help='store and diff history in file')
    parser.add_argument('-F', '--htmlfile',
                        help='if results are found, output HTML to file')
    parser.add_argument('-t', '--trim', help='specify superfluous text',
                        action='append')
    parser.add_argument('url', nargs=1, help='URL to request')
    parser.add_argument('dom_path', nargs='+',
                        help='One or more DOM paths to traverse')
    args = parser.parse_args(argv)
    # if sys.argv[0] in args.packages:
    #    args.packages.remove(sys.argv[0])
    return args


def check_args(args):
    '''
    Raises value errors if args is missing something
    '''
    if not args.url or not args.dom_path:
        raise ArgError()
    if args.verbose:
        global _is_verbose
        _is_verbose = True

    # Expand all relevant user directories
    if args.file:
        args.file = os.path.expanduser(args.file)

    if args.htmlfile:
        args.htmlfile = os.path.expanduser(args.htmlfile)

    args.url = args.url[0]


class ListItem:
    def __init__(self, elem, trims):
        text = PyQuery(elem).text()
        for trim in (trims or []):
            text = text.replace(trim, '')
        self.rx = re.compile(r'\W')
        self.text = text
        self.trimmed_text = self.rx.sub(' ', text)
        self.html = PyQuery(elem).html()
        self.normalized_text = self.rx.sub('', text.lower())

    def __str__(self):
        return self.trimmed_text


def process_items(dom_paths, doc, trims):
    items = []
    for dom_path in dom_paths:
        dom_items = doc(dom_path)
        if _is_verbose:
            print('Found %i for "%s"' % (len(dom_items), dom_path))
        for dom_item in dom_items:
            items.append(ListItem(dom_item, trims))
    return items


def parse_lines(lines):
    items = []
    for line in lines:
        if '|' not in line:
            continue
        normalized, _, _ = line.partition('|')
        items.append(normalized)
    return items


def load_file_as_set(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path) as f:
        lines = f.readlines()
    return set(parse_lines(lines))


def save_items_to_file(file_path, items):
    lines = []
    for item in items:
        lines.append('%s|%s' % (item.normalized_text, repr(item.html)))
    text = '\n'.join(lines)
    with open(file_path, 'a+') as f:
        f.write('\n\n----------\n')
        f.write(str(datetime.datetime.now()))
        f.write('\n----------\n')
        f.write(text)


def store_and_remove_seen(file_path, items):
    seen = load_file_as_set(file_path)
    new_items = []
    for item in items:
        if item.normalized_text not in seen:
            new_items.append(item)
    if _is_verbose:
        print('New items (%i)' % len(new_items))
        print('Old items (%i)' % (len(items) - len(new_items)))
    if new_items:
        if _is_verbose:
            print('Saving new items to %s' % file_path)
        save_items_to_file(file_path, new_items)
    return new_items


def main(args):
    try:
        check_args(args)
    except ArgError:
        parser.print_usage()
        sys.exit(1)

    if _is_verbose:
        print('Querying "%s"' % args.url)
    doc = PyQuery(url=args.url)
    items = process_items(args.dom_path, doc, args.trim)
    if args.file:
        items = store_and_remove_seen(args.file, items)

    if not items:
        if _is_verbose:
            print('No new results, quitting')
        return

    as_text = '\n'.join([str(item) for item in items])
    as_html = '\n'.join([item.html for item in items])

    if args.html:
        print(as_html)
    else:
        print(as_text)

    if args.email:
        if _is_verbose:
            print('Sending email to ', args.email)
        send_email(args.email, as_html, as_text, len(items), args.url)

    if args.htmlfile:
        with open(args.htmlfile, 'a+') as f:
            f.write(as_html)


def send_email(email_address, html, text, count, url):
    import smtplib

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Create message container
    subject = 'Alert Scraper: %s results found' % count
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = "alertscraper@alertscraper"
    msg['To'] = email_address

    # Create the body of the message (a plain-text and an HTML version).
    text_body = '''
        %s results found for %s

        %s
    ''' % (count, url, text)

    html_body = '''
    <html>
    <head></head>
    <body>
        <p>%s results found for %s</p>
        %s
    </body>
    </html>
    ''' % (count, url, html)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's
    # address and message to send - here it is sent as one string.
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    if _is_verbose:
        # print('EMAIL ----\n', msg.as_string(), '\n----------\n')
        print('From:', msg['From'])
        print('To:', msg['To'])
        print('Subject:', msg['Subject'])

    s.quit()


def cli():
    args = list(sys.argv)

    # Hacks to get it to work in script situation
    if args and args[0].endswith('alertscraper'):
        args.pop(0)

    if __file__ in args:
        args.remove(__file__)

    main(parse_args(args))


if __name__ == '__main__':
    cli()
