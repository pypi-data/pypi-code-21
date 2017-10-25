"""Import the catalog and initial clients from a 'bon de command' csv.

To be run with: bin/zopectl run ...import_catalog.py <csv>.
"""
from sys import argv
from csv import reader
from itertools import izip
from decimal import Decimal
from re import compile, I

from transaction import commit

r = reader(open(argv[1], "rb"))

# skip lines until we find "PRODUITS"
for l in r:
  if l[0] == "PRODUITS": break

# create clients
from dm.zope.reseller.client import Clients
cm = Clients() # client management
for cl in l[5:]:
  cl = cl.strip().decode("utf-8")
  if cl and not cm.list((("title", cl),)):
    u = cm.add_item(title=cl)

# create articles
from dm.zope.reseller.article import Articles
am = Articles()
fields = "title description provider_order_no price_3 price_1".split()
kg_l = compile(r"(\d+)\s*(kg|l)$", I).match
seen = set()
for l in r:
  if l[0].strip() == "PRODUITS": continue
  if not l[1]: continue
  info = dict(izip(fields, l))
  ono = info["provider_order_no"]
  if ono in seen: print "seen", info; continue
  seen.add(ono)
  if info["price_3"].strip(): tax_code = 3; price = info["price_3"].strip()
  elif info["price_1"].strip(): tax_code = 1; price = info["price_1"].strip()
  if not price: continue
  try: price = Decimal(price.replace(",", "."))
  except: print info; continue
  p = info["description"].replace("(","").replace(")","").strip().split("x")
  if not p: print info; continue
  try: c = map(int, p[:-1])
  except ValueError: print info; continue
  price_ratio = package_size = c[0] if c else 1
  unit = p[-1].strip()
  m = kg_l(unit)
  if m is not None:
    no = int(m.group(1))
    if 2 <= no < 10:
      # assume price in `kg` or `l`
      price_ratio *= no
  if len(c) == 2:
    unit = "%d x %s" % (c[1], unit)
    # price_ratio *= c[1]
  del info["price_3"]; del info["price_1"]
  info.update(dict(
    tax_code=tax_code,
    catalog_price=price,
    price_ratio=price_ratio,
    unit=unit,
    package_size=package_size,
    ))
  a = am.list((("provider_order_no", ono),))
  if a:
    a = a[0]
    a.update(info)
    a.store()
  else:
    u = am.add_item(info)

commit()
