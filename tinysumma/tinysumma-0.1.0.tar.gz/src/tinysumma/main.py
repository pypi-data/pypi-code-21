import pandas as pd
import tinyapi
import argparse
from getpass import getpass
import os

# collect latest data
def update(username, datadir="."):
    urls_fn = os.path.join(datadir, "urls.csv")
    subs_fn = os.path.join(datadir, "subs.csv")
    messages_fn = os.path.join(datadir, "messages.csv")

    session = tinyapi.Session(username, getpass())
    messages = session.get_messages()
    urls = session.get_urls()
    subs = session.get_subscribers()

    # each of the above is a list of potentially nested dicts. Make tidy
    # ignore private keys starting with __. For urls, that's it.
    filtered_urls = [filter_private_keys(url) for url in urls]
    # probably not the most performant to make a dataframe just to immediately
    # toss into a csv...
    # bug currently in pandas where to_csv encoding default is system (e.g.,
    # cp-1252 on windows), not utf-8:
    # https://github.com/pandas-dev/pandas/issues/17097
    # so, explicitly use utf-8.

    pd.DataFrame(filtered_urls).to_csv(urls_fn, encoding="utf8")
    # dicts in subs contain two subdicts, 'stats' and 'data'. We only care
    # about 'stats'.
    for sub in subs:
        del sub['data']
    flat_filter_subs = [flatten_dict(filter_private_keys(sub)) for sub in subs]
    pd.DataFrame(flat_filter_subs).to_csv(subs_fn, encoding="utf8")

    # for messages, also dump extra cruft of ['stats']['most_clicked_urls'] --
    # duplicated by data in urls.
    for message in messages:
        del message['stats']['most_clicked_urls']
    flat_filter_ms = [flatten_dict(filter_private_keys(m)) for m in messages]
    pd.DataFrame(flat_filter_ms).to_csv(messages_fn, encoding="utf8")
    
def flatten_dict(dd, separator='_', prefix=''):
    # from https://stackoverflow.com/a/19647596/4280216
    return { prefix + separator + k if prefix else k : v
             for kk, vv in dd.items()
             for k, v in flatten_dict(vv, separator, kk).items()
             } if isinstance(dd, dict) else { prefix : dd }

def filter_private_keys(d):
    filt_keys = [k for k in d.keys() if k[:2]!="__"] 
    filt_d = {filt_key: d[filt_key] for filt_key in filt_keys}
    return filt_d

def latest_issue(datadir="."):
    m_fn = os.path.join(datadir, "messages.csv")
    # count number of lines in csv to determine number of messages, then just
    # call numbered_issue().
    with open(m_fn) as f:
        totalissues = (sum(1 for _ in f)) - 1 # subtract header line
    latest = numbered_issue(totalissues, datadir=datadir)
    return latest

def numbered_issue(n, datadir="."):
    m_fn = os.path.join(datadir, "messages.csv")
    df = pd.read_csv(m_fn)
    issue = df.sort_values("sent_at", ascending=True).iloc[n-1]
    print("Your issue, '{}', was opened by {} unique subscribers. "
          "That's a {} open rate!".format(issue.subject,
                                          issue.stats_unique_opens,
                                          issue.stats_open_rate))
    message_id = issue.id
    message_query = "message_id=={}".format(message_id)

    url_fn = os.path.join(datadir, "urls.csv")
    urls = pd.read_csv(url_fn)
    popular_url = urls.query(message_query).sort_values("total_clicks",
                                                        ascending=False).iloc[0]
    print('The most popular url was {}, with {} total '
          'clicks.'.format(popular_url.url, popular_url.total_clicks))
    clicked_urls = (urls.query("{} and total_clicks>0".format(message_query))
                        .shape[0])
    print('A total of {} urls were clicked.'.format(clicked_urls))
    return issue

def command():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--latestissue", help="print stats latest issue",
                       action="store_true")
    parser.add_argument("-n", "--numberedissue", help="print stats for "
                        "numbered issue (first=1)", type=int)
    parser.add_argument("-u", "--updateletter", help="download latest stats "
                        "to *.csv", metavar="LETTERNAME")
    parser.add_argument("--datadir", help="data directory (if not current dir)")
                       
    args = parser.parse_args()
    if args.datadir:
        datadir = args.datadir
    else:
        datadir = "."
    if args.updateletter:
        update(args.updateletter, datadir)
    if args.latestissue:
        latest_issue(datadir)
    if args.numberedissue:
        numbered_issue(args.numberedissue, datadir)

if __name__ == "__main__":
    command()
