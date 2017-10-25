# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Database access."""
from itertools import chain

from zope.interface import implements
from zope.component import getUtility
from zope.rdb.interfaces import IZopeDatabaseAdapter

from dm.zope.schema.dataschema import SchemaDict, RemoveMethods

from ..interfaces import ICollection, IObject, tagger


def dictify(cursor_or_description, row):
  """return a mapping for *row* described by *cursor_or_description*.

  Return `None`, if *row* is `None`.
  """
  if row is None: return
  description = cursor_or_description.description if hasattr(cursor_or_description, "description") else cursor_or_description
  return dict((d.name, unicode(v, "utf-8") if d.type_code == 25 and v else v)
              for (d, v) in zip(description, row)
              )


class Db(object):
  """Mixin class to provide database access."""
  def cursor(self):
    return getUtility(IZopeDatabaseAdapter, name="reseller")().cursor()


class Table(Db):
  implements(ICollection)

  # to be overridden by derived classes
  _FACTORY_ = None # the object factory
  _TABLE_ = None # the table name (including the database schema)

  # may be overridden
  _CONTEXT_ = () # attribute names to be transfered to items

  # may be overridden
  _SELECT_PATTERN_ = "select t.* from %(table)s as t where %(cond)s %(order)s"
  _ORDER_ = ""
  _GROUP_ = False
  _INITIAL_PARAMS_ = ()

  # _CONTEXT_FIELD_MAP_
  #  If not `None` a mapping which maps item fields to our attributes
  #  Used when the deriving class inherits both `Table` and `ObjectBase`
  #  and the collection depends on the base object.
  _CONTEXT_FIELD_MAP_ = None

  # _INSTANCE_CONDITION_
  # Instance specific conditions
  _INSTANCE_CONDITION_ = ()


  def add_item(self, _r_=None, **kw):
    kw["_keep_readonly_"] = True
    info = self._resolve(_r_, kw)
    if "id" in info: del info["id"]
    if not info: raise ValueError("empty data record")
    __traceback_info__ = info
    c = self.cursor()
    c.execute("insert into %s(%s) values(%s) returning id"
              % (self._TABLE_,
                 ", ".join(info.iterkeys()),
                 ", ".join("%s" for k in info.iterkeys())
                 ),
              info.values()
              )
    return c.fetchone()[0]

  def update_item(self, _id_or_r_=None, **kw):
    info = self._resolve(_id_or_r_, kw)
    if not info: return
    __traceback_info__ = info
    c = self.cursor()
    c.execute("update %s set %s where id=%%s"
              % (self._TABLE_,
                 ", ".join("%s=%%s" % k for k in info.iterkeys())
                 ),
              info.values() + [info["id"],]
              )
    if c.cursor.rowcount != 1: raise KeyError(info["id"])

  def get_item(self, id, default=None):
    ol = self.list((("id", id),), active_only=False)
    if not ol:
      if type(default) is type and issubclass(default, Exception): raise default(id)
      return default
    return ol[0]

  def list(self, condition=(), order='', active_only=True):
    table = self._TABLE_
    # determine context condition
    cfm = self._CONTEXT_FIELD_MAP_
    context_condition = () if cfm is None else \
        ((f, getattr(self, a)) for (f, a) in cfm.iteritems())
    # initial parameters
    params = [getattr(self, p) for p in self._INITIAL_PARAMS_]
    # condition
    cl = []
    if active_only: cl.append("t.active")
    for c in chain(self._INSTANCE_CONDITION_, context_condition, condition):
      f, v, op = (tuple(c) + ("=",))[:3]
      if "." not in f: f = "t." + f # alias
      if v is None and op in ("=", "!="):
        cl.append("%s is %s null" % (f, "" if op == "=" else "not"))
      else:
        cl.append("%s %s %%s" % (f, op))
        params.append(v)
    cond = " and ".join(cl) if cl else " true "
    # order
    if order.startswith("!"):
      # full order spec
      order = [order[1:]]
    else:
      # simplified order spec
      order = order.replace("+", "").split()
      for i, o in enumerate(order):
        if o.endswith("-"): order[i] = o[:-1] + " desc"
    if self._ORDER_: order.append(self._ORDER_)
    order = ", ".join(order)
    if order: order = "order by " + order
    # grouping support
    if self._GROUP_:
      fields = self._item_fields_()
      base_fields = (
        f for f in fields if not tagger.get(fields[f], "informational")
        )
      base_group = ", ".join("t." + f for f in base_fields)
    # search
    c = self.cursor()
    c.execute(self._SELECT_PATTERN_ % locals(), params)
    return [self._to_object(dictify(c, r)) for r in c.fetchall()]

  def deactivate_item(self, id):
    self.update_item(id, active=None, _keep_readonly_=True)

  def _resolve(self, _id_or_r_, kw):
    fields = self._item_fields_()
    if self._FACTORY_._SCHEMA_.providedBy(_id_or_r_):
      info = dict(
        (k,v) for (k,v)
        in ((k, getattr(_id_or_r_, k, self)) for k in fields)
        if v is not self
        )
    elif hasattr(_id_or_r_, "items"): info = dict(_id_or_r_)
    else: info = dict(id = _id_or_r_)
    keep_readonly = kw.pop("_keep_readonly_", False)
    info.update(kw)
    # add context fields
    #  Note: unless `keep_readonly` they are likely be filtered out again
    cfm = self._CONTEXT_FIELD_MAP_
    if cfm is not None:
      for f, a in cfm.iteritems(): info[f] = getattr(self, a)
    for f, v in self._INSTANCE_CONDITION_: info[f] = v
    # filter out informational/readonly fields; detect unknown fields
    #   Should we check that readonly fields are unchanged rather than
    #   just ignore them?
    unknown = []
    for k in info.keys():
      f = fields.get(k)
      if f is None: unknown.append(k); continue
      if k == "id": continue # keep "id" (important for update)
      if (f.readonly and not keep_readonly) or tagger.get(f, "informational"):
        del info[k]
    if unknown: raise KeyError(unknown)
    return info

  def _to_object(self, info):
    if info is None: return
    obj = self._FACTORY_(self, info)
    for ca in self._CONTEXT_: setattr(obj, ca, getattr(self, ca))
    return obj

  def _item_fields_(self):
    """The fields of our items."""
    return RemoveMethods(self._FACTORY_._SCHEMA_)
    

class ObjectBase(SchemaDict):
  """Base class for objects representing data records."""
  implements(IObject)

  def __init__(self, manager, *args, **kw):
    self._manager = manager
    super(ObjectBase, self).__init__(*args, **kw)

  def store(self):
    """make the current object state persistent.

    We may want to make this automatic.
    """
    self._manager.update_item(self, _keep_readonly_=True)

  def deactivate(self):
    self.active = None
    self._manager.deactivate_item(self.id)

  def reload(self): self.update(self._manager.get_item(self.id))
      
  

def store_handler(obj, event): obj.store()
