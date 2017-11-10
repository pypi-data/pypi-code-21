# coding: utf-8

from pony.orm import Database, Required

db = Database()
print(db)


class Person(db.Entity):
    username = Required(str, 50)

