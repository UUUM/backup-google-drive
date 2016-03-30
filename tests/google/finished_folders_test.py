import sqlite3

import pytest

from gdsync.google.finished_folders import FinishedFolders


@pytest.mark.usefixtures('delete_db_file')
class TestFinishedFolders:
    def test_conn(self):
        folders = FinishedFolders()
        conn = folders.conn
        assert isinstance(conn, sqlite3.Connection)

        cur = conn.execute('''
            select name from sqlite_master where type = ? AND name = ?
        ''', ('table', 'finished_folders'))
        assert 'finished_folders' == cur.fetchone()[0]

    def test_load_save(self):
        folders = FinishedFolders()

        # load no data
        folders = FinishedFolders()
        folders.load()
        assert len(folders) == 0

        # add 'foo'
        folders.add('foo')
        assert 'foo' in folders
        folders.save()

        # check if only 'foo' exists
        ids = set()
        sql = 'select id from finished_folders'
        for row in folders.conn.execute(sql):
            ids.add(row[0])
        assert 'foo' in ids
        assert len(ids) == 1

        # add 'bar'
        folders.add('bar')
        assert 'bar' in folders
        folders.save()

        # check if both 'foo' and 'bar' exist
        ids = set()
        sql = 'select id from finished_folders'
        for row in folders.conn.execute(sql):
            ids.add(row[0])
        assert 'foo' in ids
        assert 'bar' in ids
        assert len(ids) == 2
