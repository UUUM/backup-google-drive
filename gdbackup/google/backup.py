from dateutil import parser
import os
import time

from gdbackup.google.drive import Drive, Resource
from gdbackup.google.finished_folders import FinishedFolders

FinishedFolders.db_file_name = 'backup.db'


class Backup:
    def __init__(self):
        self.callback = print_none
        self.drive = Drive()

    def create_date_folder(self, res):
        folder_name = time.strftime("%Y-%m-%d")
        return res.create_folder(folder_name, unique=True)

    def find_prev_folder(self, dest_folder, cur_folder):
        cur_created_time = parser.parse(cur_folder.createdTime)
        for file in dest_folder.list(order_by='createdTime desc'):
            if not file.is_folder():
                continue

            if cur_folder.id == file.id:
                continue

            if cur_created_time <= parser.parse(file.createdTime):
                continue

            return file

        return None

    def merge(self, src, dest):
        src = self._init_resource(src)
        dest = self._init_resource(dest)

        merge = Merge(self, src, dest)
        merge.callback = self.callback
        merge.merge()

    def sync(self, src, dest, prev=None):
        src = self._init_resource(src)
        dest = self._init_resource(dest)
        prev = self._init_resource(prev)

        sync = Sync(self, src, dest, prev)
        sync.callback = self.callback
        sync.sync()

    def _init_resource(self, res):
        if isinstance(res, Resource) or res is None:
            return res
        elif isinstance(res, str):
            return self.drive.open(res)
        else:
            raise ValueError('Value must be Resource object or resource id')


class Merge:
    def __init__(self, drive, src, dest):
        self.drive = drive
        self.callback = print_none

        self.src = src
        self.dest = dest

    def merge(self):
        self._merge(self.src, self.dest, '')

    def _merge(self, src_res, dest_res, folder_name):
        folder_name = os.path.join(folder_name, dest_res.name)

        for src_item in src_res.list():
            self._merge_item(src_item, dest_res, folder_name)

    def _merge_item(self, src_item, dest_res, folder_name):
        if src_item.is_folder():
            self._merge_folder(src_item, dest_res, folder_name)
        elif src_item.is_app():
            pass
        else:
            self._merge_file(src_item, dest_res, folder_name)

    def _merge_folder(self, src_item, dest_res, folder_name):
        dest_folder = dest_res.find_folder(src_item.name)
        if not dest_folder:
            dest_folder = dest_res.create_folder(src_item.name)

        self.callback(src_item, folder_name, state='folder')
        self._merge(src_item, dest_folder, folder_name)

    def _merge_file(self, src_item, dest_res, folder_name):
        dest_file = dest_res.find(src_item.name, mime_type=src_item.mimeType)
        if not dest_file:
            self.callback(src_item, folder_name, state='new')
            src_item.copy_to(dest_res)
        elif parser.parse(dest_file.createdTime) < parser.parse(src_item.modifiedTime):
            self.callback(src_item, folder_name, state='update')
            dest_file.delete()
            src_item.copy_to(dest_res)
        else:
            self.callback(src_item, folder_name, state='skip')


class Sync:
    def __init__(self, drive, src, dest, prev=None):
        self.drive = drive
        self.callback = print_none

        self.src = src
        self.dest = dest
        self.prev = prev

        self.finished_folders = FinishedFolders(self.dest.id)
        self.finished_folders.load()

    def sync(self):
        self._sync(self.src, self.dest, self.prev, '')

    def _sync(self, src_res, dest_res, prev_res, folder_name):
        folder_name = os.path.join(folder_name, dest_res.name)

        for src_item in src_res.list():
            self._sync_item(src_item, dest_res, prev_res, folder_name)

    def _sync_item(self, src_item, dest_res, prev_res, folder_name):
        if src_item.is_folder():
            self._sync_folder(src_item, dest_res, prev_res, folder_name)
        elif src_item.is_app():
            pass
        else:
            self._sync_file(src_item, dest_res, prev_res, folder_name)

    def _sync_folder(self, src_item, dest_res, prev_res, folder_name):
        if src_item.id in self.finished_folders:
            self.callback(src_item, folder_name, state='skip')
            return

        dest_folder = dest_res.find_folder(src_item.name)
        if not dest_folder:
            dest_folder = dest_res.create_folder(src_item.name)

        if prev_res:
            prev_folder = prev_res.find_folder(src_item.name)
        else:
            prev_folder = None

        self.callback(src_item, folder_name, state='folder')
        self._sync(src_item, dest_folder, prev_folder, folder_name)

        self.finished_folders.add(src_item.id)
        self.finished_folders.save()

    def _sync_file(self, src_item, dest_res, prev_res, folder_name):
        if dest_res.find(src_item.name, mime_type=src_item.mimeType):
            return

        if prev_res:
            prev_file = prev_res.find(src_item.name, mime_type=src_item.mimeType)
        else:
            prev_file = None

        if prev_file:
            if parser.parse(prev_file.createdTime) < parser.parse(src_item.modifiedTime):
                self.callback(src_item, folder_name, state='update')
                src_item.copy_to(dest_res)
            else:
                self.callback(src_item, folder_name, state='add')
                prev_file.add_to(dest_res)
        else:
            self.callback(src_item, folder_name, state='update')
            src_item.copy_to(dest_res)


def print_none(src_item, folder_name, state=''):
    pass
