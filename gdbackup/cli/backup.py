import os
from pprint import pprint

from googleapiclient.errors import HttpError

import gdbackup
import gdbackup.google.backup
from gdbackup.config import Config


class Backup():
    def __init__(self):
        self.backup = gdbackup.google.backup.Backup()
        self.backup.callback = self._print

        self.config = Config()

    def sync(self):
        try:
            self._sync_all()
        except HttpError as error:
            self._error(error)

    def _error(self, error):
        print(error.uri)
        pprint(error.resp)
        raise error

    def _print(self, src_item, folder_name, state=''):
        name = os.path.join(folder_name, src_item.name)
        if src_item.is_folder():
            name += '/'

        print('%s: %s' % (state, name))

    def _sync(self, src_id):
        backup = self.backup
        drive = backup.drive

        src_res = drive.open(src_id)
        dest_res = drive.open(self.config['sync']['destination_id'])

        dest_folder = dest_res.create_folder(src_res.name)
        date_folder = backup.create_date_folder(dest_folder)
        prev_folder = backup.find_prev_folder(dest_folder, date_folder)
        backup.sync(src_res, date_folder, prev_folder)

    def _sync_all(self):
        for src_id in self.config['sync']['source_ids']:
            self._sync(src_id)


def main():
    Backup().sync()
