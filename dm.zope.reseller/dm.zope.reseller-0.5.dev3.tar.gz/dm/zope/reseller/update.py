# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Update handling.

Versions are identified by integers.

The current code version is given by the `VERSION` definition
in this module. The current database version is specified
by `config[-2].value` in the database (or is 1, if this does not exist).
This module contains functions `update*i*` to update the database
version from *i* to *i+1*.
"""

VERSION = 3

from config import Config

_md = globals()

_VERSIONS = None

def versions():
  """The current code and database versions."""
  global _VERSIONS
  if _VERSIONS is None:
    c = Config()
    try: dbv = int(c.get_item(-2, KeyError).value)
    except KeyError: dbv = 1
    _VERSIONS = VERSION, dbv
  return _VERSIONS


def update():
  global _VERSIONS
  c = Config()
  dbv = versions()[-1]
  while dbv < VERSION:
    _md["update%d" % dbv]()
    dbv += 1
    c.update_item(id=-2, value=dbv)
    _VERSIONS = None


def update1():
  c = Config().cursor()
  # create the config database
  c.execute("create table reseller.config(title text not null, value text) inherits(reseller.item)")
  # add `version` config information
  c.execute("insert into reseller.config(id, title, value, active) values (-2, 'version', '1', FALSE)")
##  # adapt the data model for stock support
##  c.execute("alter table reseller.client_delivery_item add article_id int not null")
##  c.execute("update reseller.client_delivery_item set article_id = (select article_id from reseller.provider_delivery_item where id = provider_delivery_item_id)")
##  c.execute("alter table reseller.client_delivery_item drop provider_delivery_item_id")
##  c.execute("alter table reseller.client_delivery alter provider_delivery_id drop not null")
  # stock support (second trial)
  c.execute("create table reseller.stock_manual(article_id int not null, units int not null, account_date timestamp default current_timestamp)")
  c.execute("""
create view reseller.stock as
  select article_id, sum(units) as units from
    (select article_id, units from reseller.stock_manual
     union all
     select pdi.article_id as article_id, cdi.units as units
       from reseller.client_delivery_item as cdi
       join reseller.client_delivery as cd on (cd.id = cdi.client_delivery_id)
       join reseller.provider_delivery_item as pdi on (pdi.id = cdi.provider_delivery_item_id)
       where cdi.active and cd.client_id = -1
    ) as t
    group by article_id
    having sum(units) != 0
    """)
  

def update2():
  c = Config().cursor()
  # create table `account_item`
  c.execute("""
create table reseller.account_item(
  client_id int not null, -- references client
  amount decimal(10,2) not null,
  account_date timestamp default current_timestamp,
  note text
) inherits(reseller.item)
""")


