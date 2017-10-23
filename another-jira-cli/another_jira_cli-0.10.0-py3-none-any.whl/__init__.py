#!/usr/bin/env python

import os
import re
import sys
import csv
import json
from pprint import pformat

import arrow
import click
import yaml
from dotmap import DotMap
from jira.exceptions import JIRAError

from .tools import print_table_from_dict, cfg_read_config
from .tools import save_config, get_hour_min, check_file_present
from .parsehelpers import parse_date_str, parse_start_time_str
from .jirahelpers import add_worklog
from .jirahelpers import catch_jira_errors
from .jirahelpers import check_for_alias
from .jirahelpers import construct_create_dict
from .jirahelpers import get_jira
from .jirahelpers import get_ticket_object
from .jirahelpers import get_worklogs_for_date_and_user
from .jirahelpers import perform_search
from .jirahelpers import search_wrapper
from .workloghelpers import log_csv, log_yaml, calculate_logged_time_for


# ============================================================================
# VERSION
# ============================================================================


__version__ = "0.10.0"


# ============================================================================
# CLICK HELP PARAMETER
# ============================================================================


CLI_HELP = dict(help_option_names=['-h', '--help'])


# ============================================================================
# COMMANDS START HERE
# ============================================================================


@click.group()
def cli():
    pass


@cli.command(context_settings=CLI_HELP)
def version():
    """
    Print the version and exits.
    """
    print(__version__)


@cli.command(context_settings=CLI_HELP)
@click.option("--jira-url", prompt=True,
              default=lambda: os.environ.get("JIRA_URL", ''))
@click.option("--username", prompt=True,
              default=lambda: os.environ.get("JIRA_USER", ''))
@click.option("--password", prompt=True,
              hide_input=True,
              default=lambda: os.environ.get("JIRA_PASSWORD", ''))
def init(**kwargs):
    """
    Needs to be called one time to initialize URL, user and password.
    """
    save_config(kwargs)


@cli.command(context_settings=CLI_HELP)
@click.argument("search-aliases", nargs=-1, required=True)
def lookup(search_aliases):
    """
    Call a previously saved search.

    You can combine multiple defined aliasesto do things like this:

    $ jira lookup prj-in-progress due-1m

    That will combine the search alias 'prj-in-progress' with the alias 'due1m'.
    Internally this happens (roughly):

      [(filter0)[, AND (filter1) ...]] AND (ORIGINAL_QUERY)

    So you can emulate your board behavior :)

    *IMPORTANT NOTE*

    Please make sure that AT MOST ONE QUERY contains an "ORDER BY" part. We
    handle the rest.
    """
    config = cfg_read_config()
    saved_searches = config.get("saved_searches", {})
    use_queries = []
    if search_aliases[0] not in saved_searches:
        print("No such search alias: '{}'".format(search_aliases[0]))
        sys.exit(-1)
    use_queries.append(saved_searches[search_aliases[0]])
    for falias in search_aliases[1:]:
        if falias not in saved_searches:
            print("Search filter '{}' not defined.")
            sys.exit(-1)
        use_queries.append(saved_searches[falias])
    # now, sort that the ORDER BY thing is last

    def sortfunc(x): return 1 if " order by" in x.lower() else 0
    use_queries = list(sorted(use_queries, key=sortfunc))
    # now, find the order by clause, and move it OUT of those brackets.
    # for now we don't check if there's only one ...
    order_clause = ""
    if " order by " in use_queries[-1].lower():
        order_query = use_queries[-1]
        pos = order_query.lower().find("order ")
        order_clause = order_query[pos:]
        use_queries[-1] = order_query[:pos]
    use_queries = list(map(lambda x: "(" + x + ")", use_queries))
    jql_string = " AND ".join(use_queries) + " " + order_clause
    perform_search(jql_string)


@cli.command(name="remove-search", context_settings=CLI_HELP)
@click.argument("search-alias")
def remove_search(search_alias):
    """
    Remove a search alias.
    """
    config = cfg_read_config()
    if "saved_searches" not in config \
            or search_alias not in config["saved_searches"]:
        print("No such search alias: '{}'".format(search_alias))
        sys.exit(-1)
    del config["saved_searches"][search_alias]
    save_config(config)
    print("Saved search '{}' removed.".format(search_alias))


@cli.command(name="list-searches", context_settings=CLI_HELP)
def list_searches():
    """
    List all saved searches.
    """
    config = cfg_read_config()
    if "saved_searches" not in config:
        print("No saved searches.")
        sys.exit(-1)
    print_table_from_dict(config["saved_searches"],
                          header=("alias", "search query"))


@cli.command(name="clear-searches", context_settings=CLI_HELP)
def clear_searches():
    """
    Delete all saved searches.
    """
    config = cfg_read_config()
    if "saved_searches" not in config:
        print("No saved searches.")
        sys.exit(-1)
    del config["saved_searches"]
    save_config(config)
    print("All saved searches cleared.")


@cli.command(context_settings=CLI_HELP)
@click.argument("searchstring", nargs=-1)
@click.option("--save-as", default=None)
@click.option("--just-save", is_flag=True)
def search(searchstring, save_as, just_save):
    """
    Search for header or summary text.

    If you specify --save-as, the query is executed and - on success - saved
    as a search alias which you recall using the 'lookup' command later.

    If you additionally specify --just-save, the search is just saved as alias
    but not executed ('just saved', right? :).
    """
    query = " ".join(searchstring)
    query = "summary ~ \"{}\" OR description ~\"{}\"".format(query)
    search_wrapper(query, save_as, just_save)


@cli.command(context_settings=CLI_HELP)
@click.argument("jql_string", nargs=-1)
@click.option("--save-as", default=None)
@click.option("--just-save", is_flag=True)
def jql(jql_string, save_as, just_save):
    """
    Search for tickets using JQL.

    If you specify --save-as, the query is executed and - on success - saved
    as a search alias which you recall using the 'lookup' command later.

    If you additionally specify --just-save, the search is just saved as alias
    but not executed ('just saved', right? :).
    """
    query = " ".join(jql_string)
    search_wrapper(query, save_as, just_save)


@cli.command(name="cleanup-day", context_settings=CLI_HELP)
@click.argument("date")
@click.option("--day-start", default="0900",
              help="When the first worklog should start. "
                   "Format must be HHMM.")
def cleanup_day(date, day_start):
    """
    Arrange the worklogs nicely for a given day.

    This means that it will re-sort all the logged time entries to follow one
    after another, so that it looks nice in the JIRA calendar view.

    The original order is *tried* to be preserved, if the logs start at the
    exact same moment the ticket key is used as second indicator, then the
    worklog duration (descending).
    """
    date_obj = parse_date_str(date)
    start_h, start_m = parse_start_time_str(day_start)
    start_time = date_obj.floor('day').replace(hour=start_h, minute=start_m)
    tickets_and_logs = get_worklogs_for_date_and_user(date_obj)
    # [(WORKLOG, TICKET), ...]
    tuples = [(v, sl[0]) for sl in tickets_and_logs for v in sl[1]]
    # sort by started date, then ticket key

    def sortfunc(x): return x[0].started + x[1].key + \
        "{:08d}".format(1000000 - x[0].timeSpentSeconds)
    tuples = sorted(tuples, key=sortfunc)
    for wlog, ticket in tuples:
        next_time = start_time.replace(seconds=+int(wlog.timeSpentSeconds))
        print("{:<5} - {:<5}:  {:<10}  {}".format(
            start_time.format("HH:MM"), next_time.format("HH:MM"),
            ticket.key,
            wlog.comment if hasattr(wlog, "comment") and wlog.comment
            else "<no comment given>"
        ))
        wlog.update({'started': start_time.format("YYYY-MM-DDTHH:MM:SS.SSSZ")})
        start_time = next_time


@cli.command(name="log-time", context_settings=CLI_HELP)
@click.argument("ticket")
@click.argument("logdata", nargs=-1)
@click.option("--comment", default=None)
@click.option("--nono", is_flag=True,
              help="Don't actually log, just print the info")
def log_time(ticket, logdata, comment, nono):
    """
    Create a work log entry in a ticket.

    The general way of specifying the LOGDATA is:

        WORKLOG_STRING(1h) DATE(current day) START_TIME(0900)

    The values of the defaults are in brackets. You can specify the DATE using
    several ways: "m1", "m3", ... means (m)inus 1 day, (m)inus 3 days, etc. So
    this is yesterday and three days ago. "1", "3" means the 1st or the 3rd of
    the current month, "0110" is the 10th of January this year, and "20150110"
    is the same date in the year 2015.

    Examples (all examples will log on ticket IO-1234):

    \b
      - [...] IO-1234                    (log 1h today, starting at 0900)
      - [...] IO-1234 "2h 4m"            (log "2h 4m" today, starting at 0900)
      - [...] IO-1234 1.5h m3            (log 1.5h three days ago, ...)
      - [...] IO-1234 1.5h 12            (1.5h, at the 12th this month)
      - [...] IO-1234 1.5h 0112          (1.5h at the 12th of Jan)
      - [...] IO-1234 1.5h 20160112      (same, but 2016)
      - [...] IO-1234 1.5h 20160112 1000 (same, but work log starts at 1000)

    """
    # logdata must be: HOURS DATE START_TIME
    logdata_default = ("1h", None, "0900")
    use_worklog = logdata + logdata_default[len(logdata):]
    worklog, date, start = use_worklog
    arr = parse_date_str(date)
    use_hour, use_minute = parse_start_time_str(start)
    arr = arr.replace(hour=use_hour, minute=use_minute, second=0)
    use_datetime = arr.datetime
    # TODO - remove default timezone!!
    print("DATE           :  {}".format(arr.to('Europe/Berlin').format()))
    print("WORKLOG STRING : '{}'".format(worklog))
    print("WORKLOG COMMENT: {}".format("'{}'".format(comment)
                                       if comment else '<empty>'))
    if nono:
        print("Stopping here. No log was performed.")
    else:
        add_worklog(ticket, use_datetime, worklog, comment)


@cli.command(name="log-time-file", context_settings=CLI_HELP)
@click.argument("file")
@click.option("-dl", "--delimiter", default=';',
              help="delimiter for csv file")
def log_fromfile(file, delimiter):
    jira = get_jira()
    if '.csv' in file:
        log_csv(file, jira, delimiter)
    elif '.yaml' in file:
        log_yaml(file, jira)


@cli.command(context_settings=CLI_HELP)
@click.argument("ticket_id")
@click.argument("alias_name")
@click.option("--nocheck", is_flag=True,
              help="Don't try to check whether the ticket actually exists")
@catch_jira_errors
def alias(ticket_id, alias_name, nocheck=False):
    """
    Create an alias name for a ticket.

    That alias can be used to log time on instead of the ticket name.
    """
    config = cfg_read_config()
    if not nocheck:
        jira = get_jira()
        jira.issue(ticket_id)
    if "aliases" not in config:
        config["aliases"] = {}
    config["aliases"][alias_name] = ticket_id
    save_config(config)
    print("Alias '{}' -> '{}' created successfully."
          .format(alias_name, ticket_id))


@cli.command(context_settings=CLI_HELP)
@click.argument("alias_name")
def unalias(alias_name):
    """
    Remove a ticket alias.
    """
    config = cfg_read_config()
    if "aliases" not in config or alias_name not in config["aliases"]:
        print("No such alias: '{}'".format(alias_name))
    else:
        del config["aliases"][alias_name]
        save_config(config)
        print("Alias '{}' removed.".format(alias_name))


@cli.command(name="list-aliases", context_settings=CLI_HELP)
def list_aliases():
    """
    List all ticket aliases.
    """
    config = cfg_read_config()
    if "aliases" not in config or len(config["aliases"]) == 0:
        print("No aliases defined.")
    else:
        print_table_from_dict(config["aliases"])


@cli.command(name="clear-aliases", context_settings=CLI_HELP)
def clear_aliases():
    """
    Remove ALL ticket aliases.
    """
    config = cfg_read_config()
    if "aliases" not in config or len(config["aliases"]) == 0:
        print("No aliases defined.")
    else:
        del config["aliases"]
        save_config(config)
        print("All aliases cleared.")


@cli.command(name="fill-day", context_settings=CLI_HELP)
@click.argument("date", default=None)
@click.option("--comment", default=None,
              help="Optional worklog comment")
@click.option("--day-hours", default=8.0)
@click.option("--day-start", default="0900",
              help="The start time of the day, format HHMM")
@click.option("--default", default=None,
              help="Specify a different default ticket")
@click.option("--re-init", is_flag=True,
              help="Re-enter the default ticket")
def fill_day(date, comment, day_hours, day_start, default, re_init):
    """
    "Fill" a day with a worklog.

    This command uses a 'default' ticket to log work on. It checks how much work
    was already logged on a given day, and then creates a worklog which uses the
    remaining available time.

    You can specify how long a day is FOR ONE EXECUTION using the
    --day-hours parameter, which takes a float argument (--day-hours 8.5). The
    default (which can't be changed right now) is 8.0.

    You can also specify a different default ticket to use FOR ONE EXECUTION
    using the --default option.

    If the day is not at all filled, the log entry will start at 09:00h, which
    you can adjust by using the --day-start option (which needs to be formatted
    HHMM).

    If 'date' is not given, it uses the present day.
    """
    start_h, start_m = parse_start_time_str(day_start)
    start_time = parse_date_str(date).floor('day')\
                                     .replace(hour=start_h, minute=start_m)
    config = cfg_read_config()
    if "fill_day" not in config or re_init:
        print("Enter default ticket to use (may be an alias): ", end="")
        default_ticket_str = input()
        # just try to see if it exists
        get_ticket_object(default_ticket_str)
        config["fill_day"] = {'default_ticket': default_ticket_str}
        save_config(config)
    else:
        default_ticket_str = config["fill_day"]["default_ticket"] \
            if not default \
            else default
    ticket_and_logs = get_worklogs_for_date_and_user(start_time)
    logged_work_secs = calculate_logged_time_for(ticket_and_logs)
    # calculate log metadata
    available_secs = day_hours * 60 * 60 - logged_work_secs
    in_hours, in_mints = get_hour_min(available_secs)
    # calculate latest starting point
    just_worklogs = [v for sublist in ticket_and_logs for v in sublist[1]]
    if len(just_worklogs) > 0:
        calculated_start_time = max([arrow.get(wl.started)
                                          .replace(seconds=wl.timeSpentSeconds)
                                     for wl in just_worklogs])
        if calculated_start_time < start_time.ceil('day'):
            # if logging was shit we could be in "tomorrow" already
            start_time = calculated_start_time
    # sanity checks
    if available_secs <= 60:
        print("You have already {}h {}m logged, not filling up."
              .format(*get_hour_min(logged_work_secs)))
    else:
        log_string = "{}h {}m".format(in_hours, in_mints)
        print("Adding {} to reach {} hours on {}."
              .format(log_string, day_hours, start_time.format("MMM Do")))
        comment = "[FUP] " + comment if comment else "[FUP]"
        add_worklog(default_ticket_str, start_time, log_string, comment)
        print("Logged {} on ticket {}."
              .format(log_string, default_ticket_str))


@cli.command(name="list-worklogs", context_settings=CLI_HELP)
@click.argument("date", default=None)
def list_worklogs(date):
    """
    List all logs for a given day.
    """
    date_obj = parse_date_str(date)
    tickets_and_logs = get_worklogs_for_date_and_user(date_obj)
    logged_work_secs = calculate_logged_time_for(tickets_and_logs)
    # create a list like [(log_entry, ticket_obj), ...]
    tuples = [(v, sl[0]) for sl in tickets_and_logs for v in sl[1]]
    for log, ticket in sorted(tuples, key=lambda x: x[0].started):
        t_start = arrow.get(log.started).strftime("%H:%M")
        t_hrs, t_min = get_hour_min(log.timeSpentSeconds)
        cmt = log.comment \
            if hasattr(log, "comment") and log.comment \
            else "<no comment entered>"
        print("{:<8} {:<8} {:<8}  {:>2}h {:>2}m   {}"
              .format(log.id, ticket.key, t_start, t_hrs, t_min, cmt))
    print("\nSUM: {}h {}m"
          .format(logged_work_secs // 3600, (logged_work_secs % 3600) // 60))


@cli.command(name="list-work", context_settings=CLI_HELP)
@click.argument("date", default=None)
def list_work(date):
    """
    List on which tickets you worked how long on a given day.
    """
    date_obj = parse_date_str(date)
    tickets_and_logs = get_worklogs_for_date_and_user(date_obj)
    # create a list like [(log_entry, ticket_obj), ...]
    calced_times = [(t, sum([x.timeSpentSeconds for x in logs]))
                    for t, logs in tickets_and_logs]
    sum_time = sum([x[1] for x in calced_times])
    for ticket, seconds in sorted(calced_times, key=lambda x: x[0].key):
        use_time = "{}h {}m".format(*get_hour_min(seconds))
        use_sum = ticket.fields.summary
        if len(use_sum) > 70:
            use_sum = use_sum[:67] + "..."
        print("{:<10} {:<8}  {}".format(ticket.key, use_time, use_sum))
    print("\nSUM: {}h {}m".format(*get_hour_min(sum_time)))


@cli.command(name="delete-worklog", context_settings=CLI_HELP)
@click.argument("ticket-id")
@click.argument("worklog-id")
@catch_jira_errors
def delete_worklog(ticket_id, worklog_id):
    """
    Delete a worklog entry by ID.

    Unfortunately you really need the ticket ID for the API it seems.
    """
    jira = get_jira()
    jira.worklog(check_for_alias(ticket_id), worklog_id).delete()


@cli.command(name="bulk-create", context_settings=CLI_HELP)
@click.argument("filename")
@click.option("--csv-dialect", default="excel",
              help="Python csv dialect to use (CSV only)")
@click.option("-t", "--filetype",
              type=click.Choice(["auto", "yaml", "json", "csv"]),
              default="auto",
              help="For files without extension")
@click.option("-l", "--limit",
              default=0,
              help="Stop after creating N entries")
@click.option("-s", "--start-at",
              default=0,
              help="Start skip the first N entries (0-based)")
@click.option("-c", "--continue", "continue_file",
              metavar="ERRORFILE",
              default="",
              help="Specify error file name to retry only the failed tickets")
@click.option("--set", "manual_fields",
              multiple=True, metavar="FIELD=VAL",
              help="Set a field value manually. Takes precedence over "
                   "input data")
@click.option("-f", "--filter", "select_filters",
              multiple=True,
              metavar="FIELDNAME=REGEX",
              default="",
              help="Select issues based on field matches. Drop the rest.")
@click.option("-d", "--dry-run",
              is_flag=True,
              help="Print tickets which would be created, but don't do "
                   "anything")
@click.option("-p", "--print", "summary",
              is_flag=True,
              help="Print short summary of each created ticket")
@catch_jira_errors
def bulk_create(filename, csv_dialect, filetype, limit, start_at,
                continue_file, manual_fields, select_filters, dry_run, summary):
    """
    Mass-create tickets from a JSON, CSV or YAML file. The file must contain
    flat keys and supports the following items:

    \b
    REQUIRED FIELDS
    * project       -> JIRA project key
    * issuetype     -> str
    * summary       -> str
    * description   -> str

    \b
    OPTIONAL FIELDS
    * labels        -> see below
    * duedate       -> YYYY-MM-DD
    * estimate      -> JIRA estimate string ("1d 4h")
    * epic_name     -> string for epic name
    * epic_link     -> JIRA ticket ID (XXX-123)

    \b
    EXPLICITLY UNSUPPORTED
    * anything regarding assignee and creator

    THE "LABELS" FIELD takes a comma-separated list of strings (a,b,c...),
    which is useful for CSV input. For YAML or JSON input the field can
    additionally be a list of strings.

    FOR CSV INPUT the script expects the first line of the CSV file to contain
    the field names, withOUT any leading comment sign (e.g. "#issuetype" or
    something similar).

    ALL OTHER KEYS are just passed 1:1 into the python jira.create_issue() API
    call, with empty fields (fields containing an empty string or None) being
    filtered out.


    IMPORTANT:

    There is *NO* semantic checking of field names or field values. So if you
    have missing fields, spelling errors, etc. this is not caught before
    jira-cli tries to create the tickets. The same goes for the wrong CSV
    dialect type.


    NOTE:

    If you get this error:

        AttributeError: 'list' object has no attribute 'values'

    ... you probably have a bad field configuration (e.g. "due" instead of
    "duedate"), **OR** that every single create failed (e.g. when continuing
    after an error).
    """
    # determine file type
    check_file_present(filename)
    filetypes = {"yml": "yaml", "yaml": "yaml", "json": "json", "csv": "csv"}
    filetype = filetypes.get(filename.lower().split(".")[-1], None)
    if not filetype:
        print("Unable to determine file type from extension.")
        sys.exit(-1)
    # get list of dicts
    with open(filename, "r") as infile:
        if filetype == "yaml":
            createme = yaml.load(infile)
        elif filetype == "json":
            createme = json.load(infile)
        elif filetype == "csv":
            reader = csv.DictReader(infile, dialect=csv_dialect)
            createme = [dict(row) for row in reader]
    if not isinstance(createme, list):
        print("'{}' must contain an array as top level element!"
              .format(filename))
        sys.exit(-1)

    # convert to indexes list.
    createme = [(idx, item) for idx, item in enumerate(createme)]

    # continue last operation? then take only those indexes which are
    # marked as failed in the error file
    if continue_file:
        check_file_present(continue_file)
        continue_file = yaml.load(open(continue_file, "r"))
        createme = [createme[error[0]] for error in continue_file]
        print("Selecting only {} failed tickets from last run"
              .format(len(createme)))

    # evaluate start_at and limit
    createme = createme[start_at:start_at + limit] \
        if limit else createme[start_at:]

    # apply selection filter
    for name_regex in select_filters:
        fieldname, sfilter = name_regex.split("=")
        regex = re.compile(sfilter, re.I)
        createme = list(filter(lambda x: regex.search(x[1][fieldname]),
                               createme))

    # evaluate --set FIELD=value
    if manual_fields:
        # https://stackoverflow.com/a/12739929/902327 :)
        update_dict = dict(s.split("=") for s in manual_fields)
        for item in createme:
            item[1].update(update_dict)

    # stop on dry runs
    if dry_run:
        yaml.safe_dump(createme, stream=sys.stdout, default_flow_style=False)
        sys.exit(1)

    # prepare ticket dicts
    indexes = [item[0] for item in createme]
    createme = [construct_create_dict(item[1]) for item in createme]

    # start
    print("Creating {} JIRA issues ... ".format(len(createme)),
          end="", flush=True)
    jira = get_jira()
    created = jira.create_issues(createme)

    # add indexes to results
    created = [(x, y) for x, y in zip(indexes, created)]

    # construct errors and successes lists with indexes
    errors = list(filter(lambda x: x[1]["error"] != None, created))
    successes = list(filter(lambda x: x[1]["error"] == None, created))

    # make successes printable
    for success in successes:
        # otherwise json complaints.
        success[1]["issue"] = str(success[1]["issue"])

    # print status
    print("done.\nCreated {} tickets, {} errors."
          .format(len(created) - len(errors), len(errors)))

    # print tickets if needed
    if summary and successes:
        print("\n{:>3}   {:>10}   {}".format("NO", "ID", "SUMMARY"))
        for ticket in successes:
            tmp = DotMap(ticket[1])
            print("{:>3}   {:>10}   {}".format(ticket[0],
                                               tmp.issue,
                                               tmp.input_fields.summary))
        print()

    # write log files
    timestamp = arrow.utcnow().format('X')
    for name, results in (("created", successes), ("errors", errors)):
        if results:
            log_file = "jira-{}.{}.yaml".format(timestamp, name)
            with open(log_file, "w") as outfile:
                outfile.write(yaml.safe_dump(results, indent=2))
            print("Wrote '{}'".format(log_file))
    if errors:
        print("You can re-try only failed tickets using: "
              "--continue {}".format(log_file))
        sys.exit(1)

    # finally done :)


def console_entrypoint():
    """
    The console entrypoint, pretty much unused.
    """
    cli()
