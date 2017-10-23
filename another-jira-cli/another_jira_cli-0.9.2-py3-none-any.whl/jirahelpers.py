import sys
from functools import lru_cache, wraps

import arrow
import jira

from .tools import cfg_read_config, cfg_save_search


# ============================================================================
# DECORATORS
# ============================================================================


def catch_jira_errors(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except jira.JIRAError as e:
            print("JIRA ERROR: {}".format(e.text))
            sys.exit(-1)
    return inner


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


@lru_cache()
def get_jira():
    """
    Creates the global jira object, cached.

    :return: The JIRA object instance to use for JIRA calls.
    """
    config = cfg_read_config()
    jobj = jira.JIRA(config['jira_url'],
                     basic_auth=(config['username'],
                                 config['password']))
    return jobj


def check_for_alias(ticket_alias_str, no_output=False):
    """
    Checks whether the ticket string is an alias, if yes resolves it, if
    no returns it unchanged.

    :param ticket_alias_str: The potential ticket alias
    :param no_output: No output please
    :return: The input or the resolved alias
    """
    config = cfg_read_config()
    if "aliases" in config and ticket_alias_str in config["aliases"]:
        # we have an alias, use it.
        ticket = config["aliases"][ticket_alias_str]
        if not no_output:
            print("Resolving alias '{}' to ticket {}"
                  .format(ticket_alias_str, ticket))
        return ticket
    else:
        return ticket_alias_str


def get_tickets_logged_on_date(date: arrow.arrow.Arrow, user=None) -> list:
    """
    Uses the query 'worklogDate = "DATE" and worklogAuthor = currentUser()' to
    determine which tickets the user logged on a specific DATE.

    From the docs:

    jira.search_issues(jql_str, startAt=0, maxResults=50,
                       validate_query=True,
                       fields=None, expand=None, json_result=None)

    That should do it.

    :param date: The date as arrow object
    :param jira_obj: The JIRA object to use for querying
    :return: A list of tickets
    """
    date_str = date.format("YYYY-MM-DD")
    jql_query = 'worklogDate = "{}" and worklogAuthor = {}'\
                .format(date_str, user if user else "currentUser()")
    jira_obj = get_jira()
    tickets_on_date = jira_obj.search_issues(jql_query)
    # now we have all tickets which contain worklogs by us on a date. now let's
    # get the worklogs.
    # this is not a list.
    return tickets_on_date


def get_worklogs_for_date_and_user(date, user=None):
    """
    Retrieves all work logs for a given user on a given day. Returns a
    list of the form: [[TICKET_OBJ, [WORKLOG0,...], ...]

    :param date: The date to search worklogs for
    :param user: The user to search worklogs for
    :return: The dict as described above
    """
    config = cfg_read_config()
    if not user:
        user = config["username"]
    jira = get_jira()
    logged_tickets = get_tickets_logged_on_date(date, user)
    worklogs = [(ticket, jira.worklogs(ticket.key))
                for ticket in logged_tickets]
    # this gives us all worklogs for all the tickets. now we need to ...
    # ... filter by author and date boundaries
    lb = date.floor('day')
    ub = date.ceil('day')
    final_logs = []
    for info_tuple in worklogs:
        wls = info_tuple[1]
        wls = filter(lambda x: x.author.name == user, wls)
        wls = list(filter(lambda x: lb < arrow.get(x.started) < ub, wls))
        if len(wls) > 0:
            final_logs.append((info_tuple[0], wls))
    # remove empty tickets :)
    return final_logs


@lru_cache()
def get_ticket_object(ticket_str, no_output=False):
    """
    Returns a ticket object from a ticket key or a defined alias. The alias
    name has preference if somebody named an alias after a ticket.

    Will throw an exception if the alias or ticket can't be found.

    :param ticket_str: The ticket key or alias name.
    :param no_output: Whether to be silent while doing it.
    :return: A JIRA issue object
    """
    ticket_str = check_for_alias(ticket_str)
    jira = get_jira()
    ticket_obj = jira.issue(ticket_str)
    return ticket_obj


def add_worklog(ticket_str, use_datetime, worklog, comment,
                no_output=False):
    """
    Wrapper to add a timelog to JIRA. Mainly used to resolve a possible
    ticket alias in the process.

    :param ticket_str: The ticket identifier as string
    :param use_datetime: A datetime object with the start time and date
    :param worklog: The worklog time as used in JIRA (e.g. "1h 30m")
    :param comment: An optional comment
    :param no_output: If we should be silent
    :return:
    """
    jira = get_jira()
    ticket_obj = get_ticket_object(ticket_str, no_output)
    jira.add_worklog(ticket_obj,
                     started=use_datetime,
                     timeSpent=worklog,
                     comment=comment)


def perform_search(jql):
    try:
        jira = get_jira()
        results = jira.search_issues(jql)
        print("# {:<10} {:<20} {}".format("key", "author", "summary"))
        for result in results:
            sum = result.fields.summary
            aut = str(result.fields.reporter)
            use_sum = sum if len(sum) < 70 else sum[:67] + "..."
            use_aut = aut if len(aut) < 20 else aut[:17] + "..."
            print("{:<12} {:<20} {}".format(result.key, use_aut, use_sum))
    except jira.JIRAError as e:
        print("Search string: {}".format(jql))
        print("ERROR: {}".format(e.text))
        sys.exit(-1)


def search_wrapper(searchstring, save_as, just_save):
    if not just_save:
        perform_search(searchstring)
    if save_as:
        cfg_save_search(save_as, searchstring)


tdict = {
    #format:
    # field name:   (target field name,     conversion function)
    "labels":       ("labels",              lambda v: list(filter(None, v.split(",")))          ),
    "project":      ("project",             lambda v: {"key": v}                                ),
    "issuetype":    ("issuetype",           lambda v: {"name": v[0].upper() + v[1:].lower()}    ),
    "estimate":     ("timetracking",        lambda v: {"originalEstimate": v}                   ),
    "epic_link":    ("customfield_10018",   lambda v: v                                         ),
    "epic_name":    ("customfield_10020",   lambda v: v                                         ),
}

def construct_create_dict(input_dict):
    """
    returns the dict object which can be used to create the jira issue
    using the API.

    understands the following keys:

      - labels (comma separated list)
      - due (iso date)
      - estimate (jira estimate string)
      - issuetype
      - project
      - epic_name
      - epic_link

    all other fields are simply taken as-is.
    """
    create = {}
    for k, v in input_dict.items():
        if k in tdict:
            newkey, conv_func = tdict[k]
            create[newkey] = conv_func(v)
        else:
            create[k] = v

    # filter out empty values
    create = {k: v for k, v in create.items() if v}

    return create
