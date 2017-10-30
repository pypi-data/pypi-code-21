import unittest
import psycopg2
from breezeblocks import Database, Table
from breezeblocks.sql.join import LeftJoin
from breezeblocks.sql.operators import Equal_, In_
from breezeblocks.sql.values import QmarkStyleValue as Value

import os
DB_PATH = 'postgres://Q:ElephantQ@localhost:5432/Q'

class PostgresLibraryTests(unittest.TestCase):
    """Tests using Postgres on the Library Database."""
    
    def setUp(self):
        """Performs necessary Postgres setup"""
        self.db = Database('postgres://Q:ElephantQ@localhost:5432/Q', psycopg2)
        self.tables = {
            'Book': Table('Book', ['Id', 'Title', 'GenreId']),
            'Genre': Table('Genre', ['Id', 'Name']),
            'Author': Table('Author', ['Id', 'Name']),
            'BookAuthor': Table('BookAuthor', ['BookId', 'AuthorId'])
        }
    
    def test_tableQuery(self):
        q = self.db.query(self.tables['Author'])
    
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Id'))
            self.assertTrue(hasattr(row, 'Name'))
    
    def test_columnQuery(self):
        q = self.db.query(self.tables['Book'].getColumn('Title'))
    
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Title'))
            self.assertFalse(hasattr(row, 'GenreId'))
    
    def test_leftJoin(self):
        tbl_book = self.tables['Book']
        tbl_genre = self.tables['Genre']
        
        tbl_leftJoinBookGenre = LeftJoin(
            tbl_book, tbl_genre, on=[Equal_(
                tbl_book.getColumn('GenreId'),
                tbl_genre.getColumn('Id')
            )])
        
        q = self.db.query(
            tbl_leftJoinBookGenre.left.getColumn('Title'),
            tbl_leftJoinBookGenre.right.getColumn('Name').as_('GenreName')
        )
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Title'))
            self.assertTrue(hasattr(row, 'GenreName'))
    
    def test_orderByNullsFirst(self):
        tbl_book = self.tables['Book']
        
        q = self.db.query(tbl_book.getColumn('Title'), tbl_book.getColumn('GenreId'))\
            .order_by(tbl_book.getColumn('GenreId'), nulls='FIRST')\
            .order_by(tbl_book.getColumn('Title'))
        
        prev_genre = None
        for row in q.execute():
            if prev_genre is not None:
                self.assertIsNotNone(row.GenreId)
            prev_genre = row.GenreId
    
    def test_orderByNullsLast(self):
        tbl_book = self.tables['Book']
        
        q = self.db.query(tbl_book.getColumn('Title'), tbl_book.getColumn('GenreId'))\
            .order_by(tbl_book.getColumn('GenreId'), nulls='LAST')\
            .order_by(tbl_book.getColumn('Title'))
        
        rows = q.execute()
        prev_genre = rows[0].GenreId
        for row in rows:
            if prev_genre is None:
                self.assertIsNone(row.GenreId)
            prev_genre = row.GenreId
