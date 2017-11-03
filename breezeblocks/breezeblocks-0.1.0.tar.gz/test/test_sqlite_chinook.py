import unittest
import sqlite3
from breezeblocks import Database, Table
from breezeblocks.exceptions import QueryError
from breezeblocks.sql.aggregates import Count_, RecordCount
from breezeblocks.sql.join import InnerJoin, LeftJoin, CrossJoin
from breezeblocks.sql.operators import Equal_, In_
from breezeblocks.sql.values import QmarkStyleValue as Value

import os
DB_URL = os.path.join(os.path.dirname(__file__), 'Chinook.sqlite')

class SQLiteChinookTests(unittest.TestCase):
    """Tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        
        self.db = Database(DB_URL, sqlite3)
        self.tables = {
            'Artist': Table('Artist', ['ArtistId', 'Name']),
            'Genre': Table('Genre', ['GenreId', 'Name']),
            'Album': Table('Album', ['AlbumId', 'Title', 'ArtistId']),
            'Track': Table('Track',
                ['TrackId', 'Name', 'AlbumId', 'MediaTypeId', 'GenreId', 'Composer', 'Milliseconds', 'Bytes', 'UnitPrice']),
            'Playlist': Table('Playlist', ['PlaylistId', 'Name'])
        }
    
    def test_tableQuery(self):
        """Tests a simple select on a table."""
        q = self.db.query(self.tables['Artist'])
        
        # Assertion checks that all columns in the table are present in
        # each row returned.
        for row in q.execute():
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Name'))
    
    def test_columnQuery(self):
        """Tests a simple select on a column."""
        q = self.db.query(self.tables['Artist'].getColumn('Name'))
    
        # Assertion checks that only the queried columns are returned.
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Name'))
            self.assertFalse(hasattr(row, 'ArtistId'))
    
    def test_simpleWhereClause(self):
        """Tests a simple where clause."""
        tbl_genre = self.tables['Genre']
        tbl_track = self.tables['Track']
        genre_id = self.db.query(tbl_genre)\
            .where(tbl_genre.getColumn('Name') == Value('Alternative & Punk'))\
            .execute()[0].GenreId
    
        q = self.db.query(tbl_track.getColumn('GenreId'))\
                .where(tbl_track.getColumn('GenreId') == Value(genre_id))
    
        # Assertion checks that the where condition has been applied to
        # the results of the query.
        for track in q.execute():
            self.assertEqual(genre_id, track.GenreId)
    
    def test_nestedQueryInWhereClause(self):
        tbl_album = self.tables['Album']
        tbl_genre = self.tables['Genre']
        tbl_track = self.tables['Track']
    
        genre_id = self.db.query(tbl_genre)\
            .where(tbl_genre.getColumn('Name') == Value('Alternative & Punk'))\
            .execute()[0].GenreId
    
        q = self.db.query(tbl_album.getColumn('Title'))\
                .where(
                    In_(
                        tbl_album.getColumn('AlbumId'),
                        self.db.query(tbl_track.getColumn('AlbumId'))\
                            .where(tbl_track.getColumn('GenreId') == Value(genre_id))
                    )
                )
    
        # No assertion here because subqueries because subqueries in the select
        # clause have not been implemented.
        # However, the query running without error is important to test.
        q.execute()
    
    def test_aliasTable(self):
        tbl_album = self.tables['Album']
        tbl_artist = self.tables['Artist']
        
        artist_id = self.db.query(tbl_artist.getColumn('ArtistId'))\
            .where(Equal_(tbl_artist.getColumn('Name'), Value('Queen')))\
            .execute()[0].ArtistId
        
        musician = tbl_artist.as_('Musician')
        q = self.db.query(musician).where(Equal_(musician.getColumn('ArtistId'), Value(artist_id)))
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Name'))
            self.assertEqual(artist_id, row.ArtistId)
    
    def test_selectFromQuery(self):
        tbl_album = self.tables['Album']
        tbl_artist = self.tables['Artist']
        
        artist_id = self.db.query(tbl_artist.getColumn('ArtistId'))\
            .where(Equal_(tbl_artist.getColumn('Name'), Value('Queen')))\
            .execute()[0].ArtistId
        
        inner_q = self.db.query(tbl_album.getColumn('ArtistId'), tbl_album.getColumn('Title'))\
            .where(Equal_(tbl_album.getColumn('ArtistId'), Value(artist_id)))
        
        q = self.db.query(inner_q.as_('q'))
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Title'))
            self.assertEqual(artist_id, row.ArtistId)
    
    def test_groupBy(self):
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('GenreId'), Count_(tbl_track.getColumn('TrackId')).as_('TrackCount'))\
            .group_by(tbl_track.getColumn('GenreId'))
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'GenreId'))
            self.assertTrue(hasattr(row, 'TrackCount'))
    
    def test_having(self):
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('GenreId'), Count_(tbl_track.getColumn('TrackId')).as_('TrackCount'))\
            .group_by(tbl_track.getColumn('GenreId'))\
            .having(Count_(tbl_track.getColumn('TrackId')) > Value(25))
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'GenreId'))
            self.assertTrue(hasattr(row, 'TrackCount'))
            self.assertLess(25, row.TrackCount,
                'The track count should be greater than specified in the'\
                'having clause.'
            )
    
    def test_havingMustHaveGroupBy(self):
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('GenreId'), Count_(tbl_track.getColumn('TrackId')).as_('TrackCount'))\
            .having(Count_(tbl_track.getColumn('TrackId')) > Value(25))
        
        with self.assertRaises(QueryError):
            q.execute()
    
    def test_orderByAsc(self):
        tbl_artist = self.tables['Artist']
        
        q = self.db.query(tbl_artist.getColumn('Name'))\
            .order_by(tbl_artist.getColumn('Name'))
        
        rows = q.execute()
        prev_name = rows[0].Name
        for row in rows:
            self.assertLessEqual(prev_name, row.Name)
            prev_name = row.Name
    
    def test_orderByDesc(self):
        tbl_artist = self.tables['Artist']
        
        q = self.db.query(tbl_artist.getColumn('Name'))\
            .order_by(tbl_artist.getColumn('Name'), ascending=False)
        
        rows = q.execute()
        prev_name = rows[0].Name
        for row in rows:
            self.assertGreaterEqual(prev_name, row.Name)
            prev_name = row.Name
    
    # NULLS { FIRST | LAST } syntax not supported by SQLite currently.
    # def test_orderByNullsFirst(self):
    #     pass
    
    # NULLS { FIRST | LAST } syntax not supported by SQLite currently.
    # def test_orderByNullsLast(self):
    #     pass
    
    def test_limit(self):
        limit_amount = 5
        
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('Name'))\
            .limit(limit_amount)
        
        rows = q.execute()
        self.assertLessEqual(len(rows), limit_amount,
            'Number of rows should not be more than the limit amount.')
    
    def test_limitAndOffset(self):
        limit_amount = 100
        tbl_track = self.tables['Track']
        
        q0 = self.db.query(tbl_track.getColumn('TrackId'))\
            .order_by(tbl_track.getColumn('TrackId'))\
            .limit(limit_amount)
        q1 = self.db.query(tbl_track.getColumn('TrackId'))\
            .order_by(tbl_track.getColumn('TrackId'))\
            .limit(limit_amount, limit_amount)
        
        id_set = set(r.TrackId for r in q0.execute())
        
        for row in q1.execute():
            self.assertTrue(row.TrackId not in id_set,
                'Using offset should result in different data being'
                'returned than that of a non-offset query.'
            )
    
    def test_distinct(self):
        # Uses album 73 (Eric Clapton Unplugged) because it has multiple genres
        # of track on the album. It just seems a bit less trivial than most
        # albums as a test case.
        album_id = 73
        tbl_track = self.tables['Track']
        
        q0 = self.db.query(tbl_track.getColumn('GenreId'))\
            .where(tbl_track.getColumn('AlbumId') == Value(album_id))
        
        q1 = self.db.query(tbl_track.getColumn('GenreId'))\
            .where(tbl_track.getColumn('AlbumId') == Value(album_id))\
            .distinct()
        
        genres0 = set(row.GenreId for row in q0.execute())
        genres1 = [row.GenreId for row in q1.execute()]
        self.assertEqual(len(genres0), len(genres1),
            'Set of all genres in the album should be the same size as'
            'the list of genres retrieved with SELECT DISTINCT.'
        )
    
    def test_innerJoin(self):
        tbl_genre = self.tables['Genre']
        tbl_track = self.tables['Track']
    
        tbl_joinGenreTrack = InnerJoin(tbl_track, tbl_genre, using=['GenreId'])
    
        q = self.db.query(
            tbl_joinGenreTrack.left.getColumn('Name').as_('TrackName'),
            tbl_joinGenreTrack.right.getColumn('Name').as_('GenreName'))\
            .from_(tbl_joinGenreTrack)\
            .where(Equal_(tbl_joinGenreTrack.right.getColumn('Name'), Value('Classical')))
    
        for row in q.execute():
            self.assertEqual(2, len(row))
            self.assertTrue(hasattr(row, 'TrackName'))
            self.assertTrue(hasattr(row, 'GenreName'))
    
    def test_leftOuterJoin(self):
        tbl_album = self.tables['Album']
        tbl_track = self.tables['Track']
        
        tbl_leftJoinTrackAlbum = LeftJoin(tbl_track, tbl_album, using=['AlbumId'])
        
        q = self.db.query(
            tbl_leftJoinTrackAlbum.left.getColumn('Name'),
            tbl_leftJoinTrackAlbum.right.getColumn('Title').as_('AlbumTitle')
        )
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Name'))
            self.assertTrue(hasattr(row, 'AlbumTitle'))
    
    # Right Join not supported by SQLite currently.
    # def test_rightOuterJoin(self):
        # pass
    
    # Full Outer Join not supported by SQLite currently
    # def test_fullOuterJoin(self):
        # pass
    
    def test_crossJoin(self):
        tbl_playlist = self.tables['Playlist']
        tbl_track = self.tables['Track']
        
        playlistRecordCount = self.db.query()\
            .from_(tbl_playlist)\
            .select(RecordCount())\
            .execute()[0][0]
        
        trackRecordCount = self.db.query()\
            .from_(tbl_track)\
            .select(RecordCount())\
            .execute()[0][0]
        
        q = self.db.query()\
            .from_(CrossJoin(tbl_playlist, tbl_track))\
            .select(RecordCount().as_('RecordCount'))
        
        joinSizeRow = q.execute()[0]
        
        self.assertEqual(playlistRecordCount * trackRecordCount, joinSizeRow.RecordCount,
            'The cross join should contain as many records as '\
            'the number of playlists times the number of tracks.'
        )
