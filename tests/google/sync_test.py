# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time

import pytest

from gdsync.google.sync import Sync
from gdsync.google.drive import Drive, Resource


@pytest.mark.usefixtures('test_folder', 'src_folder', 'src_file', 'delete_db_file')
class TestSync:
    def test_init(self):
        backup = Sync('xxxxxx', 'yyyyyy')
        assert hasattr(backup.callback, '__call__')
        assert isinstance(backup.drive, Drive)
        assert isinstance(backup.src, Resource)
        assert isinstance(backup.dest, Resource)
        assert backup.finished_folders is None

    def test_sync(self, test_folder, src_folder, src_file):
        drive = Drive()
        test_folder = drive.open(test_folder.id)
        src_folder = drive.open(src_folder.id)

        sync_id = '%d' % time.time()
        dest_folder = test_folder.create_folder(sync_id)

        # sync to empty folder
        backup = Sync(src_folder, dest_folder, sync_id=sync_id).sync()
        assert len(backup.finished_folders) == 1
        assert src_folder.find('フォルダ').id in backup.finished_folders
        compare_folder(src_folder, dest_folder)

        # remove some files and sync
        dest_folder = drive.open(dest_folder.id)
        dest_folder.find('テスト', mime_type='text/plain').delete()
        dest_folder.find('テスト', mime_type='text/csv').delete()
        Sync(src_folder, dest_folder, sync_id=sync_id).sync()
        compare_folder(src_folder, dest_folder)

        # create a new file and sync
        new_file_name = '%s.txt' % sync_id
        new_file = src_folder.create(new_file_name, content='test')
        Sync(src_folder, dest_folder, sync_id=sync_id).sync()
        compare_folder(src_folder, dest_folder)

        # remove a new file and sync and a new file still exists
        new_file.delete()
        Sync(src_folder, dest_folder, sync_id=sync_id).sync()
        dest_folder = drive.open(dest_folder.id)
        assert isinstance(dest_folder.find(new_file_name), Resource)

        # skip synced folder
        dest_folder.find('フォルダ').find('テストsub').delete()
        backup = Sync(src_folder, dest_folder, sync_id=sync_id).sync()
        assert len(backup.finished_folders) == 1
        assert drive.open(dest_folder.id).find('フォルダ').find('テストsub') is None


def compare_folder(src_res, dest_res):
    drive = Drive()
    dest_res = drive.open(dest_res.id)
    src_res = drive.open(src_res.id)
    for src_item in src_res.list():
        if src_item.is_folder():
            dest_folder = dest_res.find_folder(src_item.name)
            message = '%s %s was not found' % (src_item.name, src_item.mimeType)
            assert dest_folder is not None, message
            compare_folder(src_item, dest_folder)
        else:
            dest_item = dest_res.find(src_item.name, mime_type=src_item.mimeType)
            message = '%s %s was not found' % (src_item.name, src_item.mimeType)
            assert dest_item is not None, message


def _print(src_item, folder_name, skip=False):
    name = os.path.join(folder_name, src_item.name)
    if src_item.is_folder():
        name += '/'

    if skip:
        print('Skip: ' + name)
    else:
        print(name)
