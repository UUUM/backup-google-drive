# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time

import pytest

from gdbackup.google.backup import Backup, Merge, Sync
from gdbackup.google.drive import Drive, Resource


@pytest.mark.usefixtures('test_folder', 'dest_folder')
class TestBackup:
    def test_init(self):
        backup = Backup()
        assert hasattr(backup.callback, '__call__')
        assert isinstance(backup.drive, Drive)

    def test_create_date_folder(self, dest_folder):
        backup = Backup()
        res = backup.drive.open(dest_folder.id)

        folder1 = backup.create_date_folder(res)
        assert isinstance(folder1, Resource)
        assert time.strftime("%Y-%m-%d") == folder1.name

        folder2 = backup.create_date_folder(res)
        assert isinstance(folder1, Resource)
        assert folder1.id == folder2.id

    def test_find_prev_folder(self, test_folder):
        backup = Backup()
        res = test_folder.create_folder('test_prev_folder')

        folders = []
        for i in range(3):
            folders.append(res.create_folder('folder%d' % i))
            time.sleep(1)

        folder = backup.find_prev_folder(res, folders[2])
        assert folders[1].id == folder.id

        folder = backup.find_prev_folder(res, folders[1])
        assert folders[0].id == folder.id

        folder = backup.find_prev_folder(res, folders[0])
        assert folder is None

        for folder in folders:
            folder.delete()
        res.delete()


@pytest.mark.usefixtures('dest_folder', 'src_folder', 'src_file')
class TestMerge:
    def test_merge(self, dest_folder, src_folder):
        backup = Backup()
        drive = backup.drive
        src_res = drive.open(src_folder.id)
        dest_res = drive.open(dest_folder.id)
        dest_folder = backup.create_date_folder(dest_res)

        # sync to empty folder
        merge = Merge(drive, src_res, drive.open(dest_folder.id))
        merge.merge()
        compare_folder(src_res, drive.open(dest_folder.id))

        # remove some files and merge
        dest_folder = drive.open(dest_folder.id)
        dest_folder.find('テスト', mime_type='text/plain').delete()
        dest_folder.find('テスト', mime_type='text/csv').delete()
        merge = Merge(drive, src_res, drive.open(dest_folder.id))
        merge.merge()
        compare_folder(src_res, drive.open(dest_folder.id))

        # create a new file and merge
        new_file = src_res.create('test.txt', content='test')
        merge = Merge(drive, src_res, drive.open(dest_folder.id))
        merge.merge()
        compare_folder(src_res, drive.open(dest_folder.id))
        new_file.delete()


@pytest.mark.usefixtures('dest_folder', 'src_folder', 'src_file', 'delete_db_file')
class TestSync:
    def test_sync(self, dest_folder, src_folder):
        backup = Backup()
        drive = backup.drive
        src_res = drive.open(src_folder.id)
        dest_res = drive.open(dest_folder.id)
        dest_folder = backup.create_date_folder(dest_res)

        # sync to empty folder
        sync = Sync(drive, src_res, drive.open(dest_folder.id))
        sync.sync()
        assert len(sync.finished_folders) == 1
        assert src_res.find('フォルダ').id in sync.finished_folders
        compare_folder(src_res, drive.open(dest_folder.id))

        # remove some files and sync
        dest_folder = drive.open(dest_folder.id)
        dest_folder.find('テスト', mime_type='text/plain').delete()
        dest_folder.find('テスト', mime_type='text/csv').delete()
        sync = Sync(drive, src_res, drive.open(dest_folder.id))
        sync.sync()
        compare_folder(src_res, drive.open(dest_folder.id))

        # skip synced folder
        dest_folder.find('フォルダ').find('テストsub').delete()
        sync = Sync(drive, src_res, drive.open(dest_folder.id))
        sync.sync()
        assert len(sync.finished_folders) == 1
        assert drive.open(dest_folder.id).find('フォルダ').find('テストsub') is None

        # sync to a new folder while comparing to a previous folder
        new_folder = dest_res.create_folder('new_folder')
        sync = Sync(drive, src_res, new_folder, drive.open(dest_folder.id))
        sync.sync()
        new_folder = drive.open(new_folder.id)
        dest_folder = drive.open(dest_folder.id)
        file1 = dest_folder.find('テスト', mime_type='text/plain')
        file2 = new_folder.find('テスト', mime_type='text/plain')
        assert file1.id == file2.id
        file = drive.open(new_folder.id).find('フォルダ').find('テストsub')
        assert isinstance(file, Resource)


def compare_folder(src_res, dest_res):
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
