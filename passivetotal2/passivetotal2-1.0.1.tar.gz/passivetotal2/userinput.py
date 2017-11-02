import sys
from . import Client

# argparse seems to strip out newlines, so I think we're kind of limited as to
# how much we actually need to document here.
SETUP_DESCRIPTION = 'example: passivetotal2 setup myusername@example.org abcdef1234...'
ACCOUNT_DESCRIPTION = 'example: passivetotal2 account --account'
SSL_DESCRIPTION = 'example: passivetotal2 ssl riskiq --keyword'
DNS_DESCRIPTION = 'example: passivetotal2 dns example.org riskiq.com'
TRACKERS_DESCRIPTION = 'example: passivetotal2 trackers riskiq FacebookId'
MONITOR_DESCRIPTION = 'example: passivetotal2 monitor'
HOST_DESCRIPTION = 'example: passivetotal2 host example.org --trackers -D parents'
WHOIS_DESCRIPTION = 'example: passivetotal2 whois example.org'
ENRICH_DESCRIPTION = 'example: passivetotal2 enrich example.org'
ACTION_DESCRIPTION = 'example: passivetotal2 actions classify evil.example.org -s malicious'
PROJECT_DESCRIPTION = 'example: passivetotal2 project find'
ARTIFACT_DESCRIPTION = 'example: passivetotal2 artifact find'


def _add_args(p):
    p.add_argument('--json', '-j', action='store_true',
                   help='output results as raw JSON response')
    p.add_argument('--csv', '-c', dest='write_csv', action='store_true',
                   help='output results as CSV response')
    p.add_argument('--delim', '-d', help='output fields using delimiter DELIM')
    p.add_argument('--config', help='path to client config file')
    p.add_argument('--no-headers', '-n', action='store_true',
                   help='exclude headers')
    p.add_argument('--include', '-I', help='only include these headers ' +
                   '(separate by commas)')
    p.add_argument('--exclude', '-E', help='exclude these headers ' +
                   '(separate by commas)')
    p.add_argument('--order', '-R', help='order the headers in this order ' +
                   '(separate by commas)')
    p.add_argument('--rotate', '-r', action='store_true',
                   help='rotate the table counter clockwise')
    p.add_argument('--sort', '-z', dest='sort_columns', default='firstSeen,resolve',
                   help='order the rows in this order (separate by commas)')


def _add_setup_args(subs):
    p = subs.add_parser('setup', help='configure the pt client',
                        description=SETUP_DESCRIPTION)
    p.add_argument('username', help='your passivetotal username')
    p.add_argument('key', help='your passivetotal api key')
    _add_args(p)


def _add_account_args(subs):
    p = subs.add_parser('account', help='account interface',
                        description=ACCOUNT_DESCRIPTION)
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--account', '-A', action='store_true',
                     help='get account info')
    grp.add_argument('--history', '-H', action='store_true',
                     help='get account history')
    grp.add_argument('--monitors', '-M', action='store_true',
                     help='get monitors')
    grp.add_argument('--organization', '-O', action='store_true',
                     help='get account organization')
    grp.add_argument('--quotas', '-Q', choices=('both', 'user', 'organization'),
                     nargs='?', const='both', action='store',
                     help='get account quotas')
    grp.add_argument('--sources', '-S', action='store_true',
                     help='get account sources')
    grp.add_argument('--teamstream', '-T', action='store_true',
                     help='get teamstream')
    _add_args(p)


def _add_ssl_args(subs):
    p = subs.add_parser('ssl', help='ssl interface',
                        description=SSL_DESCRIPTION)
    p.add_argument('query', help='the ssl cert query')
    grp = p.add_mutually_exclusive_group()
    grp.add_argument('--history', '-H', action='store_true',
                     help='get ssl cert history')
    grp.add_argument('--keyword', '-K', action='store_true',
                     help='search using a keyword')
    grp.add_argument('--field', '-F',
                     help='search for an ssl cert using a field')
    _add_args(p)


def _add_dns_args(subs):
    p = subs.add_parser('dns', help='passive DNS interface',
                        description=DNS_DESCRIPTION)
    p.add_argument('queries', nargs='+', help='DNS record(s) to query '
                   '(specify - to read them in from standard input')
    p.add_argument('--unique', '-u', action='store_true',
                   help='output unique entries')
    p.add_argument('--keyword', '-K', action='store_true',
                   help='search by keyword')
    _add_args(p)


def _add_trackers_args(subs):
    p = subs.add_parser('trackers', help='tracker interface',
                        description=TRACKERS_DESCRIPTION)
    p.add_argument('query', help='the tracker query')
    p.add_argument('type', choices=(
        '51laId', 'AboutmeId', 'AddThisPubId', 'AddThisUsername',
        'AuthorstreamId', 'BitbucketcomId', 'BitlyId', 'CheezburgerId',
        'ClickyId', 'ColourloversId', 'DiigoId', 'DispusId', 'EngadgetId',
        'EtsyId', 'FacebookId', 'FavstarId', 'FfffoundId', 'FlavorsId',
        'FlickrId', 'FoodspottingId', 'FreesoundId', 'GitHubId', 'GithubId',
        'GoogleAnalyticsTrackingId', 'GooglePlusId', 'GoogleTagManagerId',
        'HubpagesId', 'ImgurId', 'InstagramId', 'KloutId', 'LanyrdId',
        'LastfmId', 'LibrarythingId', 'LinkedInId', 'LinkedinId',
        'MarketinglandcomId', 'MixpanelId', 'MuckrackId', 'MyanimelistId',
        'MyfitnesspalId', 'NewRelicId', 'OptimizelyId', 'PandoraId',
        'PicasaId', 'PinkbikeId', 'PinterestId', 'PlancastId', 'PlurkId',
        'PornhubId', 'RaptorId', 'ReadabilityId', 'RedditId', 'RedtubeId',
        'SlideshareId', 'SmugmugId', 'SmuleId', 'SoundcloudId', 'SoupId',
        'SpeakerdeckId', 'SporcleId', 'StackoverflowId', 'SteamcommunityId',
        'StumbleuponId', 'ThesixtyoneId', 'TribeId', 'TripitId', 'TumblrId',
        'TwitpicId', 'TwitterId', 'UntappdId', 'UstreamId', 'WattpadId',
        'WefollowId', 'WhosAmungUsId', 'WordPressId', 'Wordpress', 'SupportId',
        'XangaId', 'Xfire', 'SocialId', 'XhamsterId', 'XvideosId',
        'YandexMetricaCounterId', 'YouTubeChannel', 'YouTubeId', 'YoutubeId',
    ), help='the type of tracker')
    _add_args(p)


def _add_monitor_args(subs):
    p = subs.add_parser('monitor', help='monitor interface',
                        description=MONITOR_DESCRIPTION)
    p.add_argument('--project', '-P', help='the project GUID')
    p.add_argument('--artifact', '-A', help='the artifact GUID')
    p.add_argument('--start', '-s', help='start datetime, example: '
                   '"2017-01-01 00:00:00"')
    p.add_argument('--end', '-e', help='end datetime, example: '
                   '"2017-01-01 00:00:00"')
    _add_args(p)


def _add_host_args(subs):
    p = subs.add_parser('host', help='host interface',
                        description=HOST_DESCRIPTION)
    p.add_argument('query', help='the domain or ip to query with')
    p.add_argument('--direction', '-D',
                   help='the direction to query in',
                   choices={'parents', 'children'})
    p.add_argument('--trackers', '-T', action='store_true',
                   help='search for trackers')
    p.add_argument('--start', '-s', help='start datetime, example: '
                   '"2017-01-01 00:00:00"')
    p.add_argument('--end', '-e', help='end datetime, example: '
                   '"2017-01-01 00:00:00"')
    _add_args(p)


def _add_whois_args(subs):
    p = subs.add_parser('whois', help='WHOIS interface',
                        description=WHOIS_DESCRIPTION)
    p.add_argument('queries', nargs='+', help='Whois record(s) to query '
                   '(specify - to read them in from standard input')
    p.add_argument('--field', '-F', help='choose field to search by',
                   choices=('domain', 'email', 'name', 'organization',
                            'address', 'phone', 'nameserver'))
    p.add_argument('--keyword', '-K', action='store_true',
                   help='search by keyword')
    _add_args(p)


def _add_enrich_args(subs):
    p = subs.add_parser('enrich', help='enrichment interface',
                        description=ENRICH_DESCRIPTION)
    p.add_argument('query', help='the artifact query')
    grp = p.add_mutually_exclusive_group()
    grp.add_argument('--malware', '-m', action='store_true',
                     help='malware search')
    grp.add_argument('--osint', '-o', action='store_true', help='osint search')
    grp.add_argument('--subdomains', '-s', action='store_true',
                     help='subdomains search')
    p.add_argument('--short', '-S', action='store_true',
                   help='show only subdomains')
    _add_args(p)

    p = subs.add_parser('bulkenrich', help='bulk enrichment interface')
    p.add_argument('queries', nargs='+', help='the enrichment queries, '
                   '(specify - to read them in from standard input')
    _add_args(p)


def _add_action_args(subs):
    p = subs.add_parser('actions',
                        help='Actions that can be applied to domains',
                        description=ACTION_DESCRIPTION)
    psubs = p.add_subparsers(dest='subcmd')
    ps = psubs.add_parser('monitor', help='Get the domain\'s monitor status')
    ps.add_argument('domain')
    # ps.add_argument('--set', choices={'True', 'False'})
    _add_args(ps)
    ps = psubs.add_parser('classify',
                          help='Get or set the domain\'s classification')
    ps.add_argument('domains', nargs='+')
    ps.add_argument('--set', '-s', choices={'malicious', 'suspicious',
                                            'non-malicious', 'unknown'})
    _add_args(ps)
    ps = psubs.add_parser('compromised',
                          help='Get or set the domain\'s compormised status')
    ps.add_argument('domain')
    ps.add_argument('--set', '-s', choices={'true', 'false'})
    _add_args(ps)
    ps = psubs.add_parser('dyndns',
                          help='Get or set the domain\'s dyndns status')
    ps.add_argument('domain')
    ps.add_argument('--set', '-s', choices={'true', 'false'})
    _add_args(ps)
    ps = psubs.add_parser('sinkhole',
                          help='Get or set the domain\'s sinkhole status')
    ps.add_argument('IP')
    ps.add_argument('--set', '-s', choices={'true', 'false'})
    _add_args(ps)

    ps = psubs.add_parser('tag', help='Tag artifact')
    psubs = ps.add_subparsers(dest='action')
    pss = psubs.add_parser('add', help='add tags to an artifact')
    pss.add_argument('query', help='the artifact')
    pss.add_argument('tags', nargs='+', help='the tags to add')
    _add_args(pss)
    pss = psubs.add_parser('set', help='set tags for an artifact')
    pss.add_argument('query', help='the artifact')
    pss.add_argument('tags', nargs='+', help='the tags to set')
    _add_args(pss)
    pss = psubs.add_parser('delete', help='delete tags from an artifact')
    pss.add_argument('query', help='the artifact')
    pss.add_argument('tags', nargs='+', help='the tags to remove')
    _add_args(pss)
    pss = psubs.add_parser('get', help='get tags for an artifact')
    pss.add_argument('query', help='the artifact')
    _add_args(pss)
    pss = psubs.add_parser('search', help='get tags for an artifact')
    pss.add_argument('tag', help='the artifact')
    _add_args(pss)


def _add_project_args(subs):
    p = subs.add_parser('project', help='use find, create, update, or delete',
                        description=PROJECT_DESCRIPTION)
    psubs = p.add_subparsers(dest='subcmd')

    ps = psubs.add_parser('find', help='find project')
    ps.add_argument('--guid', '-g', help='project UUID')
    ps.add_argument('--owner', '-o', help='owner filter for find')
    ps.add_argument('--creator', '-C', help='creator filter for find')
    ps.add_argument('--organization', '-O', help='organization filter for find')
    ps.add_argument('--visibility', '-v', choices=('public', 'private'),
                    help='project visibility')
    ps.add_argument('--featured', '-f', action='store_true',
                    help='feature project on homepage')
    _add_args(ps)

    ps = psubs.add_parser('create', help='create project')
    ps.add_argument('name', help='project name')
    ps.add_argument('visibility', choices=('public', 'private'),
                    help='project visibility')
    ps.add_argument('--description', '--desc', '-D', help='project description')
    ps.add_argument('--featured', '-f', action='store_true',
                    help='feature project on homepage')
    ps.add_argument('--tags', '-t', help='project tags')
    _add_args(ps)

    ps = psubs.add_parser('update', help='update project')
    ps.add_argument('guid', help='project UUID')
    ps.add_argument('--name', '-N', help='project name')
    ps.add_argument('--description', '--desc', '-D', help='project description')
    ps.add_argument('--visibility', '-v', choices=('public', 'private'),
                    help='project visibility')
    ps.add_argument('--featured', '-f', action='store_true',
                    help='feature project on homepage')
    ps.add_argument('--tags', '-t', help='project tags')
    _add_args(ps)

    ps = psubs.add_parser('delete', help='delete project')
    ps.add_argument('guid', help='project UUID')
    _add_args(ps)

    ps = psubs.add_parser('tag', help='tag project')
    pssubs = ps.add_subparsers(dest='action')
    pss = pssubs.add_parser('add', help='add tags to an project')
    pss.add_argument('query', help='the project')
    pss.add_argument('tags', nargs='+', help='the tags to add')
    _add_args(pss)
    pss = pssubs.add_parser('set', help='set tags for an project')
    pss.add_argument('query', help='the project')
    pss.add_argument('tags', nargs='+', help='the tags to set')
    _add_args(pss)
    pss = pssubs.add_parser('delete', help='delete tags from an project')
    pss.add_argument('query', help='the project')
    pss.add_argument('tags', nargs='+', help='the tags to remove')
    _add_args(pss)


def _add_artifact_args(subs):
    p = subs.add_parser('artifact', help='use find, create, update, or delete',
                        description=ARTIFACT_DESCRIPTION)
    psubs = p.add_subparsers(dest='subcmd')

    ps = psubs.add_parser('find', help='find artifact')
    ps.add_argument('--guid', '-g', help='artifact UUID')
    ps.add_argument('--project', '-p', help='the project guid')
    ps.add_argument('--owner', '-o', help='owner filter for find')
    ps.add_argument('--creator', '-C', help='creator filter for find')
    ps.add_argument('--organization', '-O', help='organization filter for find')
    ps.add_argument('--query', '-q', help='the query to find')
    ps.add_argument('--type', '-T', help='the artifact type')
    _add_args(ps)

    ps = psubs.add_parser('create', help='create artifact')
    ps.add_argument('project', help='the project guid')
    ps.add_argument('queries', nargs='+', help='the queries to create, '
                    'use - to read them from stdin')
    ps.add_argument('--type', '-T', help='the artifact type')
    ps.add_argument('--tags', '-t', help='artifact tags')
    _add_args(ps)

    ps = psubs.add_parser('update', help='update artifact')
    ps.add_argument('guids', nargs='+', help='the guids to update, '
                    'use - to read them from stdin')
    ps.add_argument('--monitor', '-M', choices={'true', 'false'},
                    help='Set Monitoring')
    ps.add_argument('--tags', '-t', help='artifact tags')
    _add_args(ps)

    ps = psubs.add_parser('delete', help='delete artifact')
    ps.add_argument('guids', nargs='+', help='the guids to delete, '
                    'use - to read them from stdin')
    _add_args(ps)

    ps = psubs.add_parser('tag', help='tag artifacts')
    pssubs = ps.add_subparsers(dest='action')
    pss = pssubs.add_parser('add', help='add tags to an artifact')
    pss.add_argument('query', help='the artifact')
    pss.add_argument('tags', nargs='+', help='the tags to add')
    _add_args(pss)
    pss = pssubs.add_parser('set', help='set tags for an artifact')
    pss.add_argument('query', help='the artifact')
    pss.add_argument('tags', nargs='+', help='the tags to set')
    _add_args(pss)
    pss = pssubs.add_parser('delete', help='delete tags from an artifact')
    pss.add_argument('query', help='the artifact')
    pss.add_argument('tags', nargs='+', help='the tags to remove')
    _add_args(pss)
    pss = pssubs.add_parser('get', help='get tags for an artifact')
    pss.add_argument('query', help='the artifact')
    _add_args(pss)


def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest='cmd')
    _add_account_args(subs)
    _add_ssl_args(subs)
    _add_dns_args(subs)
    _add_setup_args(subs)
    _add_trackers_args(subs)
    _add_monitor_args(subs)
    _add_host_args(subs)
    _add_whois_args(subs)
    _add_enrich_args(subs)
    _add_action_args(subs)
    _add_project_args(subs)
    _add_artifact_args(subs)

    args = parser.parse_args()
    if args.cmd == 'setup':
        return None, args

    if args.cmd not in ('dns', 'whois', 'enrich', 'bulkenrich', 'project',
                        'artifact', 'account', 'actions', 'trackers', 'ssl',
                        'monitor', 'host', 'setup'):
        parser.print_usage()
        sys.exit(1)

    try:
        if args.config:
            client = Client(config=args.config)
        else:
            client = Client()
    except:
        parser.print_usage()
        sys.exit(1)

    if args.exclude:
        args.exclude = args.exclude.split(',')
    else:
        args.exclude = []
    if args.include:
        args.include = args.include.split(',')
        args.order = args.include
    else:
        if args.order:
            args.order = args.order.split(',')

    return (client, args)
