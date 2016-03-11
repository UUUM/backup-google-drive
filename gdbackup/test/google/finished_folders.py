import sqlite3
import unittest

from gdbackup.test.google import TestCase
from gdbackup.google.finished_folders import FinishedFolders


class BackupTest(TestCase):
    def setUp(self):
        self._remove_db_file()

    def tearDown(self):
        self._remove_db_file()

    def test_conn(self):
        folders = FinishedFolders('xxxxxx')
        conn = folders.conn
        assert isinstance(conn, sqlite3.Connection)

        cur = conn.execute('''
            select name from sqlite_master where type = ? AND name = ?
        ''', ('table', 'finished_folders'))
        assert 'finished_folders' == cur.fetchone()[0]

    def test_load(self):
        folders = FinishedFolders('xxxxxx')

        # add dummy data
        sql = 'insert into finished_folders (id, root_id) values (?, ?)'
        folders.conn.execute(sql, ('foo', 1))
        folders.conn.commit()

        # load no data, ignore dummy data
        folders = FinishedFolders('xxxxxx')
        folders.load()
        assert len(folders) == 0

        # add 'foo'
        folders.add('foo')
        assert 'foo' in folders
        folders.save()

        # load
        folders = FinishedFolders('xxxxxx')
        folders.load()
        assert 'foo' in folders
        assert len(folders) == 1

    def test_save(self):
        folders = FinishedFolders('xxxxxx')

        # add 'foo'
        folders.add('foo')
        assert 'foo' in folders
        folders.save()

        # check if only 'foo' exists
        ids = set()
        sql = 'select id from finished_folders where root_id = ?'
        for row in folders.conn.execute(sql, ('xxxxxx',)):
            ids.add(row[0])
        assert 'foo' in ids
        assert len(ids) == 1

        # add 'bar'
        folders.add('bar')
        assert 'bar' in folders
        folders.save()

        # check if both 'foo' and 'bar' exist
        ids = set()
        sql = 'select id from finished_folders where root_id = ?'
        for row in folders.conn.execute(sql, ('xxxxxx',)):
            ids.add(row[0])
        assert 'foo' in ids
        assert 'bar' in ids
        assert len(ids) == 2


if __name__ == '__main__':
    unittest.main()
