import re

from .db import DB


def get_db_information_from_url(url) -> (str, int, str, str, str):
    """
    return database server host, port, user, password and database name from the connection uri.

    for ex url=mysql+pymysql://root:root@127.0.0.1:3306/master?charset=utf8mb4 (with charset)
    or url=mysql+pymysql://root:root@127.0.0.1:3306/master (without charset)
    """

    # ignore the charset part
    if "?" in url:
        url = url.split("?")[0]

    pattern = re.compile(r'''
                        (?P<name>[\w\+]+)://
                        (?:
                            (?P<username>[^:/]*)
                            (?::(?P<password>.*))?
                        @)?
                        (?:
                            (?:
                                \[(?P<ipv6host>[^/]+)\] |
                                (?P<ipv4host>[^/:]+)
                            )?
                            (?::(?P<port>[^/]*))?
                        )?
                        (?:/(?P<database>.*))?
                        ''', re.X)

    m = pattern.match(url)
    c = m.groupdict()

    return c["ipv4host"], int(c["port"]), c["username"], c["password"], c["database"]


def get_db_from_url(url) -> DB:
    """
    Get the `DB` object from a database url.

    :param url: the database url, for ex: mysql+pymysql://root:root@127.0.0.1:3306/master?charset=utf8mb4
    :return: the corresponding DB object
    """
    host, port, username, password, name = get_db_information_from_url(url)
    return DB(host, port, username, password, name)
