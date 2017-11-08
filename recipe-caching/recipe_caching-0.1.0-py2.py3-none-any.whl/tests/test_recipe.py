from dogpile.cache.region import make_region
from sqlalchemy import Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

from recipe import Dimension, Metric, Shelf, Recipe, SETTINGS
from recipe.oven import get_oven

IN_MEMORY_CACHE = {}
SETTINGS.CACHE_REGIONS = {
    'default': make_region().configure(
        'dogpile.cache.memory',
        arguments={'cache_dict': IN_MEMORY_CACHE}
    )
}

Base = declarative_base()
oven = get_oven('sqlite://', name='caching')

TABLEDEF = '''
        CREATE TABLE IF NOT EXISTS foo
        (first text,
         last text,
         age int);
'''

oven.engine.execute(TABLEDEF)
oven.engine.execute(
    "insert into foo values ('hi', 'there', 5), ('hi', 'fred', 10)")


class MyTable(Base):
    first = Column('first', String(), primary_key=True)
    last = Column('last', String())
    age = Column('age', Integer())

    __tablename__ = 'foo'
    __table_args__ = {'extend_existing': True}


mytable_shelf = Shelf({
    'first': Dimension(MyTable.first),
    'last': Dimension(MyTable.last),
    'age': Metric(func.sum(MyTable.age))
})


class TestRecipeIngredients(object):
    def setup(self):
        # create a Session
        self.session = oven.Session()
        self.shelf = mytable_shelf

    def recipe(self, **kwargs):
        return Recipe(shelf=self.shelf, session=self.session,
                      dynamic_extensions=['caching'], **kwargs)

    def test_dimension(self):
        recipe = self.recipe().metrics('age').dimensions('first')
        assert recipe.to_sql() == """SELECT foo.first AS first,
       sum(foo.age) AS age
FROM foo
GROUP BY foo.first"""
        assert recipe.all()[0].first == 'hi'
        assert recipe.all()[0].age == 15
        assert recipe.stats.rows == 1

        cached = False
        cached_key = None
        for key in IN_MEMORY_CACHE.keys():
            if str(recipe.query()) in key:
                cached = True
                cached_key = key
        assert cached
        cache = ('hi', 15)
        assert cache == IN_MEMORY_CACHE[cached_key][0][0]

    def test_dimension2(self):
        recipe = self.recipe().metrics('age').dimensions('last').order_by(
            'last')
        assert recipe.to_sql() == """SELECT foo.last AS last,
       sum(foo.age) AS age
FROM foo
GROUP BY foo.last
ORDER BY foo.last"""
        assert recipe.all()[0].last == 'fred'
        assert recipe.all()[0].age == 10
        assert recipe.stats.rows == 2

        cached = False
        cached_key = None
        for key in IN_MEMORY_CACHE.keys():
            if str(recipe.query()) in key:
                cached = True
                cached_key = key
        assert cached
        cache = ('fred', 10)
        print(IN_MEMORY_CACHE[cached_key][0][0])
        assert cache == IN_MEMORY_CACHE[cached_key][0][0]

    def test_recipe_init(self):
        recipe = self.recipe(metrics=('age',), dimensions=('last',)).order_by(
            'last')
        assert recipe.to_sql() == """SELECT foo.last AS last,
       sum(foo.age) AS age
FROM foo
GROUP BY foo.last
ORDER BY foo.last"""
        assert recipe.all()[0].last == 'fred'
        assert recipe.all()[0].age == 10
        assert recipe.stats.rows == 2

        cached = False
        cached_key = None
        for key in IN_MEMORY_CACHE.keys():
            if str(recipe.query()) in key:
                cached = True
                cached_key = key
        assert cached
        cache = ('fred', 10)
        print(IN_MEMORY_CACHE[cached_key][0][0])
        assert cache == IN_MEMORY_CACHE[cached_key][0][0]
