import os
import sqlite3

import gdsync


class FinishedFolders(set):
    db_file_name = 'default.db'
    db_file = None
    table = 'finished_folders'

    _conn = None

    def __init__(self, root_id):
        if self.db_file is None:
            self.db_file = os.path.join(gdsync.VAR_DIR, self.db_file_name)

        self.root_id = root_id

    def __exit__(self):
        if self._conn is not None:
            self._conn.close()

    @property
    def conn(self):
        if not self._conn:
            self._conn = self._connect()
            self._initialize_table()
        return self._conn

    def load(self):
        sql = 'select id from %s where root_id = ?' % self.table
        for row in self.conn.execute(sql, (self.root_id,)):
            self.add(row[0])

        return self

    def save(self):
        for id in self:
            self.conn.execute('''
                insert or replace into %s (id, root_id)
                values (?, ?)
            ''' % self.table, (id, self.root_id))
        self.conn.commit()

        return self

    def _connect(self):
        db_dir = os.path.dirname(self.db_file)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        return sqlite3.connect(self.db_file)

    def _initialize_table(self):
        self.conn.execute('''
            create table if not exists %s (
                id      text not null,
                root_id text not null,
                unique (id, root_id)
            )
        ''' % self.table)

        return self
